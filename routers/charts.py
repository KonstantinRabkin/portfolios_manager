from fastapi import APIRouter
from fastapi.responses import Response
import io
import matplotlib.pyplot as plt

from backup_utils import PORTFOLIO_HISTORY

router = APIRouter()

@router.get("/chart/{portfolio_name}")
async def chart(portfolio_name: str):
    if portfolio_name not in PORTFOLIO_HISTORY or not PORTFOLIO_HISTORY[portfolio_name]:
        buf = io.BytesIO()
        plt.figure(figsize=(2, 1))
        plt.axis("off")
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight", pad_inches=0)
        plt.close()
        buf.seek(0)
        return Response(content=buf.getvalue(), media_type="image/png")

    hist = PORTFOLIO_HISTORY[portfolio_name]
    times = [h["time"] for h in hist]
    values = [h["value"] for h in hist]

    plt.figure(figsize=(3, 1.5))
    plt.plot(times, values, color="#1976D2", linewidth=1.2)
    plt.fill_between(times, values, color="#BBDEFB")
    plt.xticks([], [])
    plt.yticks([], [])
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120)
    plt.close()
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")

