from fastapi import FastAPI, Header, HTTPException, Request
from schemas import DataModel
from ml.model_loader import load_model
from ml.inference import run_model

app = FastAPI()

model = load_model()


@app.post("/forward")
async def post_forward(
    request: Request,
    data: DataModel | None = None,
    extra_param: str | None = Header(default=None)
):
    if data is not None:
        result = run_model(model, data.dict())

        if result is None:
            raise HTTPException(
                status_code=403,
                detail="модель не смогла обработать данные"
            )

        return {"prediction": result}

    raise HTTPException(
        status_code=400,
        detail="bad request"
    )

