"""
국회 열린국회정보 MCP 서버 v4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
환경변수: ASSEMBLY_API_KEY (열린국회정보 인증키)
설치: pip install -r requirements.txt
실행: python server.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
사용 API:
  TVBPMBILL11       - 의안 검색
  BILLINFODETAIL    - 의안 심사경과 상세
  ncwgseseafwbuheph - 위원회 회의록
"""

import asyncio, json, os
from typing import Any
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

KEY  = os.environ.get("ASSEMBLY_API_KEY", "")
BASE = "https://open.assembly.go.kr/portal/openapi"
HDR  = {"User-Agent": "Mozilla/5.0 (AssemblyMCP/4.0)"}

CMMT = {
    "과방위": "과학기술정보방송통신위원회",
    "법사위": "법제사법위원회",
    "행안위": "행정안전위원회",
    "국방위": "국방위원회",
    "환노위": "환경노동위원회",
    "기재위": "기획재정위원회",
    "산자위": "산업통상자원중소벤처기업위원회",
    "복지위": "보건복지위원회",
    "교육위": "교육위원회",
    "외통위": "외교통일위원회",
    "정보위": "정보위원회",
    "여가위": "여성가족위원회",
    "농해수위": "농림축산식품해양수산위원회",
    "문체위": "문화체육관광위원회",
    "국토위": "국토교통위원회",
    "운영위": "국회운영위원회",
    "예결위": "예산결산특별위원회",
    "윤리특위": "윤리특별위원회",
}

app = Server("assembly-law-mcp")
client = httpx.AsyncClient(timeout=12, headers=HDR)

def _ck():
    if not KEY:
        raise ValueError("ASSEMBLY_API_KEY 환경변수 미설정")

def _rows(data: dict, svc: str) -> list:
    for b in data.get(svc, []):
        if isinstance(b, dict) and "row" in b:
            return b["row"]
    return []

def _total(data: dict, svc: str) -> int:
    for b in data.get(svc, []):
        if isinstance(b, dict) and "head" in b:
            return b["head"][0].get("list_total_count", 0)
    return 0

async def _get(svc: str, params: dict) -> dict:
    p = {"KEY": KEY, "Type": "json", **params}
    r = await client.get(f"{BASE}/{svc}", params=p)
    r.raise_for_status()
    return r.json()

def _cm(committee: str) -> str:
    return CMMT.get(committee, committee)

def _bill_url(bill_id: str) -> str:
    return f"https://likms.assembly.go.kr/bill/billDetail.do?billId={bill_id}"

# ──────────────────────────────────────────────
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_bill",
            description=(
                "【의안 검색】법률안명·발의자·위원회·처리상태로 의안을 검색합니다.\n"
                "위원회 약칭 가능 (과방위, 법사위, 행안위 등)\n"
                "proc_result 예시: '계류중', '가결', '부결', '대안반영폐기', '임기만료폐기'\n"
                "계류의안만 보려면 proc_result='계류중' 사용"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bill_name":    {"type": "string", "description": "법률안명 키워드 (예: 인공지능, 정보통신망)"},
                    "proposer":     {"type": "string", "description": "대표발의자"},
                    "committee":    {"type": "string", "description": "소관위원회 (약칭 가능)"},
                    "proc_result":  {"type": "string", "description": "처리결과 필터 (예: 계류중, 가결). 미입력 시 전체"},
                    "assembly_age": {"type": "string", "description": "대수 (기본: 22)", "default": "22"},
                    "limit":        {"type": "integer", "description": "조회 건수", "default": 20}
                }
            }
        ),
        Tool(
            name="get_bill_detail",
            description=(
                "【의안 상세】bill_id 또는 bill_no로 의안의 전체 심사경과를 조회합니다.\n"
                "소관위 접수/상정/처리, 법사위 처리, 본회의 처리, 공포 정보 포함.\n"
                "원문(HWP/PDF) 링크도 반환합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bill_id": {"type": "string", "description": "의안 ID (search_bill 결과의 bill_id)"},
                    "bill_no": {"type": "string", "description": "의안번호 (bill_id 대신 사용 가능)"}
                }
            }
        ),
        Tool(
            name="search_meeting_record",
            description=(
                "【위원회 회의록 검색】위원회 회의록을 검색합니다.\n"
                "year: 검색 연도 (예: '2026'). 접두사 매칭 지원 ('202'로 2020년대 전체).\n"
                "위원회명 약칭 가능."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "committee":    {"type": "string", "description": "위원회명 (약칭 가능)"},
                    "year":         {"type": "string", "description": "회의 연도 (예: 2026)", "default": "202"},
                    "keyword":      {"type": "string", "description": "회의명 또는 안건명 키워드"},
                    "assembly_age": {"type": "string", "default": "22"},
                    "limit":        {"type": "integer", "default": 10}
                }
            }
        ),
    ]

# ──────────────────────────────────────────────
@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        _ck()
        fn = {
            "search_bill":          _search_bill,
            "get_bill_detail":      _get_bill_detail,
            "search_meeting_record":_search_meeting_record,
        }[name]
        result = await fn(**arguments)
    except Exception as e:
        result = {"error": str(e), "tool": name}
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

# ── ① 의안 검색 ──────────────────────────────
async def _search_bill(bill_name="", proposer="", committee="",
                       proc_result="", assembly_age="22", limit=20) -> dict:
    cm = _cm(committee)
    data = await _get("TVBPMBILL11", {
        "pIndex": 1, "pSize": limit, "AGE": assembly_age,
        "BILL_NAME": bill_name, "PROPOSER": proposer,
        "COMMITTEE": cm, "PROC_RESULT": proc_result
    })
    rows = _rows(data, "TVBPMBILL11")
    total = _total(data, "TVBPMBILL11")
    results = [{
        "bill_id":     r.get("BILL_ID", ""),
        "bill_no":     r.get("BILL_NO", ""),
        "bill_name":   r.get("BILL_NAME", ""),
        "proposer":    r.get("PROPOSER", ""),
        "propose_dt":  r.get("PROPOSE_DT", ""),
        "committee":   r.get("CURR_COMMITTEE", ""),
        "proc_result": r.get("PASS_GUBUN", "계류의안"),
        "detail_url":  _bill_url(r.get("BILL_ID", "")),
    } for r in rows]
    return {
        "total_count": total,
        "returned": len(results),
        "query": {"bill_name": bill_name, "committee": cm or "전체", "proc_result": proc_result or "전체"},
        "results": results
    }

# ── ② 의안 상세 ─────────────────────────────
async def _get_bill_detail(bill_id="", bill_no="") -> dict:
    if not bill_id and not bill_no:
        return {"error": "bill_id 또는 bill_no 필요"}

    # bill_no → bill_id 변환
    if not bill_id and bill_no:
        data = await _get("TVBPMBILL11", {
            "pIndex": 1, "pSize": 1, "BILL_NO": bill_no, "AGE": "22"
        })
        rows = _rows(data, "TVBPMBILL11")
        if not rows:
            return {"error": f"의안번호 {bill_no}에 해당하는 의안 없음"}
        bill_id = rows[0].get("BILL_ID", "")

    data = await _get("BILLINFODETAIL", {"BILL_ID": bill_id})
    key = list(data.keys())[0] if data else "BILLINFODETAIL"
    rows = _rows(data, key)
    if not rows:
        return {"error": "해당 의안 없음", "bill_id": bill_id}
    r = rows[0]
    return {
        "bill_id":   bill_id,
        "bill_name": r.get("BILL_NM", ""),
        "bill_no":   r.get("BILL_NO", ""),
        "proposer":  r.get("PPSR", ""),
        "propose_dt":r.get("PPSL_DT", ""),
        "session":   r.get("PPSL_SESS", ""),
        "심사경과": {
            "소관위원회": r.get("JRCMIT_NM", ""),
            "소관위_접수일":  r.get("JRCMIT_CMMT_DT", ""),
            "소관위_상정일":  r.get("JRCMIT_PRSNT_DT", ""),
            "소관위_처리일":  r.get("JRCMIT_PROC_DT", ""),
            "소관위_처리결과":r.get("JRCMIT_PROC_RSLT", "계류"),
            "법사위_접수일":  r.get("LAW_CMMT_DT", ""),
            "법사위_상정일":  r.get("LAW_PRSNT_DT", ""),
            "법사위_처리일":  r.get("LAW_PROC_DT", ""),
            "법사위_처리결과":r.get("LAW_PROC_RSLT", ""),
            "본회의_상정일":  r.get("RGS_PRSNT_DT", ""),
            "본회의_의결일":  r.get("RGS_RSLN_DT", ""),
            "본회의_결과":    r.get("RGS_CONF_RSLT", ""),
            "정부이송일":     r.get("GVRN_TRSF_DT", ""),
            "공포법률명":     r.get("PROM_LAW_NM", ""),
            "공포일":        r.get("PROM_DT", ""),
            "공포번호":       r.get("PROM_NO", ""),
        },
        "links": {
            "detail": _bill_url(bill_id),
            "pdf":    f"https://likms.assembly.go.kr/filegate/servlet/FileGate?type=1&bookId={bill_id}",
            "hwp":    f"https://likms.assembly.go.kr/filegate/servlet/FileGate?type=0&bookId={bill_id}",
        }
    }

# ── ③ 회의록 검색 ────────────────────────────
async def _search_meeting_record(committee="", year="202", keyword="",
                                  assembly_age="22", limit=10) -> dict:
    cm = _cm(committee)
    params = {
        "pIndex": 1, "pSize": limit,
        "DAE_NUM": assembly_age,
        "CONF_DATE": year or "202",
    }
    if cm:
        params["COMM_NAME"] = cm
    if keyword:
        params["TITLE"] = keyword

    data = await _get("ncwgseseafwbuheph", params)
    key = list(data.keys())[0] if data else ""
    if "RESULT" in data:
        return {"error": data["RESULT"]["MESSAGE"], "params": params}

    rows = _rows(data, key)
    total = _total(data, key)
    results = [{
        "title":      r.get("TITLE", ""),
        "committee":  r.get("COMM_NAME", ""),
        "conf_date":  r.get("CONF_DATE", ""),
        "conf_no":    r.get("CONFER_NUM", ""),
        "pdf_url":    r.get("PDF_LINK_URL", ""),
        "vod_url":    r.get("VOD_LINK_URL", ""),
    } for r in rows]
    return {
        "total_count": total,
        "returned": len(results),
        "committee": cm or "전체",
        "year": year,
        "results": results
    }

# ──────────────────────────────────────────────
async def main():
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
