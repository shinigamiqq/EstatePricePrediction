import json
import time
import numpy as np
from datetime import timedelta
from typing import Optional, List

from fastapi import FastAPI, Header, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from schemas import (
    DataModel, 
    HistoryResponse, 
    HistoryItemResponse,
    StatsResponse, 
    ProcessingTimeStats, 
    InputDataStats,
    TokenResponse,
    UserLogin,
    MessageResponse
)
from ml.model_loader import load_model
from ml.inference import run_model
from database import engine, get_db, Base
from models import RequestHistory
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    require_admin,
    verify_delete_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

#  юзаем alembic

app = FastAPI(
    title="Estate Price Prediction API",
    description="API для предсказания цен недвижимости с историей запросов и статистикой",
    version="1.0.0"
)

# грузим модель при старте
model = load_model()


# Авторизация

@app.post("/login", response_model=TokenResponse, tags=["Auth"])
async def login(user_data: UserLogin):
    """
    Логин - получаем jwt токен
    тестовые данные: admin / admin123
    """
    user = authenticate_user(user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(access_token=access_token)


# Основной эндпоинт

@app.post("/forward", tags=["Prediction"])
async def post_forward(
    request: Request,
    data: DataModel | None = None,
    extra_param: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """
    Главный эндпоинт - кидаем сюда данные о квартире, получаем предсказание цены
    """
    start_time = time.time()
    
    # если данных нет - кидаем 400
    if data is None:
        raise HTTPException(
            status_code=400,
            detail="bad request"
        )
    
    # сохраняем входные данные как json строку
    input_json = json.dumps(data.dict(), ensure_ascii=False)
    
    try:
        result = run_model(model, data.dict())
        processing_time = (time.time() - start_time) * 1000  # переводим в мс
        
        if result is None:
            # модель вернула None - что-то пошло не так
            history_entry = RequestHistory(
                input_data=input_json,
                input_length=len(input_json),
                prediction=None,
                status="error",
                error_message="модель не смогла обработать данные",
                processing_time_ms=processing_time
            )
            db.add(history_entry)
            db.commit()
            
            raise HTTPException(
                status_code=403,
                detail="модель не смогла обработать данные"
            )
        
        # всё ок - сохраняем в историю
        prediction_value = result.get("prediction")
        history_entry = RequestHistory(
            input_data=input_json,
            input_length=len(input_json),
            prediction=prediction_value,
            status="success",
            error_message=None,
            processing_time_ms=processing_time
        )
        db.add(history_entry)
        db.commit()
        
        return {"prediction": result}
        
    except HTTPException:
        # если уже HTTPException - просто прокидываем дальше
        raise
    except Exception as e:
        # любая другая ошибка - логируем и кидаем 403
        processing_time = (time.time() - start_time) * 1000
        
        history_entry = RequestHistory(
            input_data=input_json,
            input_length=len(input_json),
            prediction=None,
            status="error",
            error_message=str(e),
            processing_time_ms=processing_time
        )
        db.add(history_entry)
        db.commit()
        
        raise HTTPException(
            status_code=403,
            detail="модель не смогла обработать данные"
        )


#  История

@app.get("/history", response_model=HistoryResponse, tags=["History"])
async def get_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Возвращает историю всех запросов
    skip/limit для пагинации если записей много
    """
    total_count = db.query(func.count(RequestHistory.id)).scalar()
    
    # сортируем по дате, новые сверху
    items = db.query(RequestHistory)\
        .order_by(RequestHistory.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return HistoryResponse(
        total_count=total_count,
        items=[HistoryItemResponse.model_validate(item) for item in items]
    )


@app.delete("/history", response_model=MessageResponse, tags=["History"])
async def delete_history(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_delete_token)
):
    """
    Чистит всю историю
    нужен заголовок X-Delete-Token: delete-history-secret-token
    """
    deleted_count = db.query(RequestHistory).delete()
    db.commit()
    
    return MessageResponse(message=f"Удалено {deleted_count} записей из истории")


# Статистика

@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Статистика по запросам - время обработки, квантили, инфа о входных данных
    """
    # вытаскиваем все времена обработки
    processing_times = db.query(RequestHistory.processing_time_ms).all()
    processing_times = [pt[0] for pt in processing_times if pt[0] is not None]
    
    # считаем статистику по времени
    if processing_times:
        times_array = np.array(processing_times)
        processing_time_stats = ProcessingTimeStats(
            mean=float(np.mean(times_array)),
            percentile_50=float(np.percentile(times_array, 50)),
            percentile_95=float(np.percentile(times_array, 95)),
            percentile_99=float(np.percentile(times_array, 99))
        )
    else:
        # если запросов еще не было - нули
        processing_time_stats = ProcessingTimeStats(
            mean=0.0,
            percentile_50=0.0,
            percentile_95=0.0,
            percentile_99=0.0
        )
    
    # статистика по входным данным
    total_requests = db.query(func.count(RequestHistory.id)).scalar() or 0
    successful_requests = db.query(func.count(RequestHistory.id))\
        .filter(RequestHistory.status == "success").scalar() or 0
    failed_requests = db.query(func.count(RequestHistory.id))\
        .filter(RequestHistory.status == "error").scalar() or 0
    
    avg_input_length = db.query(func.avg(RequestHistory.input_length)).scalar() or 0.0
    min_input_length = db.query(func.min(RequestHistory.input_length)).scalar() or 0
    max_input_length = db.query(func.max(RequestHistory.input_length)).scalar() or 0
    
    input_stats = InputDataStats(
        total_requests=total_requests,
        successful_requests=successful_requests,
        failed_requests=failed_requests,
        avg_input_length=float(avg_input_length),
        min_input_length=min_input_length,
        max_input_length=max_input_length
    )
    
    return StatsResponse(
        processing_time=processing_time_stats,
        input_stats=input_stats
    )


# Админка

@app.get("/admin/history", response_model=HistoryResponse, tags=["Admin"])
async def admin_get_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    История для админов (нужен jwt токен)
    """
    total_count = db.query(func.count(RequestHistory.id)).scalar()
    
    items = db.query(RequestHistory)\
        .order_by(RequestHistory.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return HistoryResponse(
        total_count=total_count,
        items=[HistoryItemResponse.model_validate(item) for item in items]
    )


@app.delete("/admin/history", response_model=MessageResponse, tags=["Admin"])
async def admin_delete_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Удаление истории для админов (нужен jwt токен)
    """
    deleted_count = db.query(RequestHistory).delete()
    db.commit()
    
    return MessageResponse(message=f"Удалено {deleted_count} записей из истории")
