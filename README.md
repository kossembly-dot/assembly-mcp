# assembly-mcp

MCP (Model Context Protocol) server for the **Korean National Assembly Open API** ([open.assembly.go.kr](https://open.assembly.go.kr)).

Search bills, track legislative progress, retrieve bill details and committee meeting records -- all from Claude Desktop or any MCP-compatible client.

## Tools

| Tool | Description |
|---|---|
| `search_bill` | Search bills by name, proposer, committee, or status |
| `get_bill_detail` | Get full legislative review history for a bill |
| `get_bill_reason` | Get the proposal reason and links to the original document |
| `get_bill_review_info` | Get committee review progress (receipt, presentation, resolution) |
| `get_pending_bills` | List currently pending bills by committee or keyword |
| `search_meeting_record` | Search committee meeting records by year, committee, or keyword |

### Tool Parameters

#### `search_bill`

| Parameter | Type | Description |
|---|---|---|
| `bill_name` | string | Bill name keyword (e.g. "인공지능", "정보통신망") |
| `proposer` | string | Lead proposer name |
| `committee` | string | Committee name (abbreviations supported) |
| `proc_result` | string | Status: "계류중", "가결", "부결", "대안반영폐기", "임기만료폐기" |
| `assembly_age` | string | Assembly number (default: "22") |
| `limit` | integer | Max results (default: 20) |

#### `get_bill_detail`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `bill_id` | string | Yes | Bill ID from `search_bill` results |

#### `get_bill_reason`

| Parameter | Type | Description |
|---|---|---|
| `bill_id` | string | Bill ID |
| `bill_no` | string | Bill number (alternative to bill_id) |

#### `get_bill_review_info`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `bill_id` | string | Yes | Bill ID |

#### `get_pending_bills`

| Parameter | Type | Description |
|---|---|---|
| `committee` | string | Committee name (abbreviations supported) |
| `bill_name` | string | Bill name keyword |
| `assembly_age` | string | Assembly number (default: "22") |
| `limit` | integer | Max results (default: 30) |

#### `search_meeting_record`

| Parameter | Type | Description |
|---|---|---|
| `committee` | string | Committee name (abbreviations supported) |
| `year` | string | Meeting year (e.g. "2026"). Prefix matching supported -- "202" matches all 2020s |
| `keyword` | string | Meeting title or agenda keyword |
| `assembly_age` | string | Assembly number (default: "22") |
| `limit` | integer | Max results (default: 10) |

## Committee Abbreviations

You can use common Korean abbreviations for committee names:

| Abbreviation | Full Name |
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

## Setup

### Prerequisites

- Python 3.10+
- An API key from [open.assembly.go.kr](https://open.assembly.go.kr) (free)

### Installation

```bash
pip install -r requirements.txt
```

### Getting an API Key

1. Visit [open.assembly.go.kr](https://open.assembly.go.kr)
2. Sign up for an account
3. Go to "인증키 신청" (API Key Application)
4. Apply for a key -- approval is instant

### Claude Desktop Configuration

#### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "assembly-law": {
      "command": "python",
      "args": ["C:\\path\\to\\assembly-mcp\\server.py"],
      "env": {
        "ASSEMBLY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "assembly-law": {
      "command": "python3",
      "args": ["/path/to/assembly-mcp/server.py"],
      "env": {
        "ASSEMBLY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Usage Examples

Once configured, you can ask Claude in Korean:

- **"과방위에 계류 중인 인공지능 관련 법안 찾아줘"** -- searches pending AI bills in the Science & ICT Committee
- **"22대 국회에서 발의된 정보통신망법 개정안 목록 보여줘"** -- lists amendments to the Information & Communications Network Act
- **"이 법안의 심사경과 알려줘"** -- shows the legislative review history
- **"법사위 최근 회의록 검색해줘"** -- searches recent Legislation & Judiciary Committee meeting records
- **"의안번호 2200001로 제안이유 조회해줘"** -- retrieves the proposal reason by bill number

## License

[MIT](LICENSE)
