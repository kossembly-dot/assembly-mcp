# assembly-mcp

**대한민국 국회 열린국회정보 API**([open.assembly.go.kr](https://open.assembly.go.kr))를 위한 MCP(Model Context Protocol) 서버입니다.

Claude Desktop 또는 MCP 호환 클라이언트에서 의안 검색, 입법 진행 현황 추적, 의안 상세 조회, 위원회 회의록 검색을 할 수 있습니다.

## 도구 목록

| 도구 | 설명 |
|---|---|
| `search_bill` | 법률안명·발의자·위원회·처리상태로 의안 검색 |
| `get_bill_detail` | 의안의 전체 심사경과 조회 (소관위→법사위→본회의→공포) |
| `get_bill_reason` | 제안이유 및 원문 링크 조회 |
| `get_bill_review_info` | 위원회 심사정보 (접수·상정·의결 일자 및 결과) 조회 |
| `get_pending_bills` | 현재 계류 중인 법률안 목록 조회 |
| `search_meeting_record` | 위원회 회의록 검색 |

### 도구별 파라미터

#### `search_bill` -- 의안 검색

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `bill_name` | string | 법률안명 키워드 (예: 인공지능, 정보통신망) |
| `proposer` | string | 대표발의자 |
| `committee` | string | 소관위원회 (약칭 가능) |
| `proc_result` | string | 처리결과: "계류중", "가결", "부결", "대안반영폐기", "임기만료폐기" |
| `assembly_age` | string | 대수 (기본: "22") |
| `limit` | integer | 조회 건수 (기본: 20) |

#### `get_bill_detail` -- 의안 상세·심사경과

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `bill_id` | string | 예 | 의안 ID (`search_bill` 결과에서 확인) |

#### `get_bill_reason` -- 제안이유 조회

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `bill_id` | string | 의안 ID |
| `bill_no` | string | 의안번호 (bill_id 대신 사용 가능) |

#### `get_bill_review_info` -- 심사정보

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `bill_id` | string | 예 | 의안 ID |

#### `get_pending_bills` -- 계류의안 목록

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `committee` | string | 위원회 (약칭 가능) |
| `bill_name` | string | 법률안명 키워드 |
| `assembly_age` | string | 대수 (기본: "22") |
| `limit` | integer | 조회 건수 (기본: 30) |

#### `search_meeting_record` -- 회의록 검색

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `committee` | string | 위원회명 (약칭 가능) |
| `year` | string | 회의 연도 (예: "2026"). 접두사 매칭 지원 -- "202"로 2020년대 전체 검색 가능 |
| `keyword` | string | 회의명 또는 안건명 키워드 |
| `assembly_age` | string | 대수 (기본: "22") |
| `limit` | integer | 조회 건수 (기본: 10) |

## 위원회 약칭 지원

자주 사용하는 위원회 약칭을 그대로 사용할 수 있습니다:

| 약칭 | 정식 명칭 |
|---|---|
| 과방위 | 과학기술정보방송통신위원회 |
| 법사위 | 법제사법위원회 |
| 행안위 | 행정안전위원회 |
| 국방위 | 국방위원회 |
| 환노위 | 환경노동위원회 |
| 기재위 | 기획재정위원회 |
| 산자위 | 산업통상자원중소벤처기업위원회 |
| 복지위 | 보건복지위원회 |
| 교육위 | 교육위원회 |
| 외통위 | 외교통일위원회 |
| 정보위 | 정보위원회 |
| 여가위 | 여성가족위원회 |
| 농해수위 | 농림축산식품해양수산위원회 |
| 문체위 | 문화체육관광위원회 |
| 국토위 | 국토교통위원회 |

## 설치 및 설정

### 사전 요구사항

- Python 3.10+
- 열린국회정보 API 인증키 ([open.assembly.go.kr](https://open.assembly.go.kr)에서 무료 발급)

### 설치

```bash
pip install -r requirements.txt
```

### API 인증키 발급

1. [open.assembly.go.kr](https://open.assembly.go.kr) 접속
2. 회원가입
3. "인증키 신청" 메뉴에서 키 신청
4. 즉시 승인되어 사용 가능

### Claude Desktop 설정

#### Windows

`%APPDATA%\Claude\claude_desktop_config.json` 편집:

```json
{
  "mcpServers": {
    "assembly-law": {
      "command": "python",
      "args": ["C:\\path\\to\\assembly-mcp\\server.py"],
      "env": {
        "ASSEMBLY_API_KEY": "발급받은-인증키"
      }
    }
  }
}
```

#### macOS

`~/Library/Application Support/Claude/claude_desktop_config.json` 편집:

```json
{
  "mcpServers": {
    "assembly-law": {
      "command": "python3",
      "args": ["/path/to/assembly-mcp/server.py"],
      "env": {
        "ASSEMBLY_API_KEY": "발급받은-인증키"
      }
    }
  }
}
```

## 사용 예시

설정 후 Claude에게 한국어로 질문하세요:

- **"과방위에 계류 중인 인공지능 관련 법안 찾아줘"**
- **"22대 국회에서 발의된 정보통신망법 개정안 목록 보여줘"**
- **"이 법안의 심사경과 알려줘"**
- **"법사위 최근 회의록 검색해줘"**
- **"의안번호 2200001로 제안이유 조회해줘"**

## 라이선스

[MIT](LICENSE)
