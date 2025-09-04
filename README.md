# Korean Map MCP (Microservice Cloud Proxy)

이 프로젝트는 [Kakao 로컬 API](https://developers.kakao.com/docs/latest/ko/local/dev-guide)를 위한 간단한 프록시 서버입니다. 클라이언트 측에 API 키를 노출하지 않고 안전하게 Kakao API를 호출할 수 있도록 중간에서 요청을 중계하는 역할을 합니다.

## ✨ 주요 기능

- **API 키 은닉**: 서버에서 Kakao API 키를 관리하여 클라이언트 측의 보안을 강화합니다.
- **간단한 엔드포인트**: Kakao API의 복잡한 URL 대신 직관적인 경로를 제공합니다.
- **요청 로깅**: 서버로 들어오는 모든 요청(메서드, 경로 등)을 로깅하여 디버깅 및 모니터링이 용이합니다.
- **상세 디버그 로그**: `LOG_LEVEL=DEBUG` 설정 시, Kakao API와의 통신 내용을 포함한 상세한 로그를 확인할 수 있습니다.
- **SSE 지원**: `/search/category` 엔드포인트는 Server-Sent Events(SSE)를 지원하여 스트림 방식의 데이터 전송이 가능합니다.

## 🚀 실행 방법

### 사전 준비

1.  **Go 설치**: Go 언어 (버전 1.21 이상)가 설치되어 있어야 합니다.
2.  **Kakao REST API 키 발급**: [Kakao Developers](https://developers.kakao.com/)에서 애플리케이션을 등록하고 REST API 키를 발급받아야 합니다.

### 실행

1.  **API 키 설정**: 발급받은 Kakao REST API 키를 환경 변수로 설정합니다.

    ```bash
    export KAKAO_API_KEY="여기에_발급받은_REST_API_키를_입력하세요"
    ```

2.  **로그 레벨 설정 (선택 사항)**: 상세한 디버그 로그를 보려면 `LOG_LEVEL`을 설정합니다.

    ```bash
    export LOG_LEVEL="DEBUG"
    ```

3.  **서버 실행**: `app` 디렉토리에서 아래 명령어를 실행하여 서버를 시작합니다.

    ```bash
    go run . # app 디렉토리 내부에서 실행
    ```

    서버가 정상적으로 시작되면 `:8080` 포트에서 요청을 수신 대기합니다.

## 📚 API 문서

모든 API는 `GET` 메서드를 사용하며, Kakao 로컬 API와 동일한 쿼리 파라미터를 지원합니다. 클라이언트는 별도의 `Authorization` 헤더 없이 MCP 서버에 요청할 수 있습니다.

### 1. 주소 검색

- **Endpoint**: `/search/address`
- **Description**: 주소 정보를 이용하여 좌표 등 상세 정보를 검색합니다.
- **Kakao API**: `v2/local/search/address.json`
- **Response Type**: `JSON`
- **Example**:
  ```bash
  curl -G "http://localhost:8080/search/address" \
    --data-urlencode "query=전북 삼성동 100"
  ```

### 2. 키워드로 장소 검색

- **Endpoint**: `/search/keyword`
- **Description**: 특정 키워드로 장소를 검색합니다.
- **Kakao API**: `v2/local/search/keyword.json`
- **Example**:
  ```bash
  curl -G "http://localhost:8080/search/keyword" \
    --data-urlencode "query=카카오프렌즈" \
    --data-urlencode "y=37.514322572335935" \
    --data-urlencode "x=127.06283102249932" \
    --data-urlencode "radius=20000"
  ```

### 3. 카테고리로 장소 검색 (SSE)

- **Endpoint**: `/search/category`
- **Description**: 미리 정의된 카테고리 코드를 이용해 장소를 검색합니다. **(SSE 스트림으로 응답)**
- **Kakao API**: `v2/local/search/category.json`
- **Example**:
  ```bash
  curl -G "http://localhost:8080/search/category" \
    --data-urlencode "category_group_code=PM9" \
    --data-urlencode "radius=20000" \
    --data-urlencode "x=127.06283102249932" \
    --data-urlencode "y=37.514322572335935"
  ```

### 4. 좌표 → 주소 변환

- **Endpoint**: `/geo/coord2address`
- **Description**: 좌표를 이용하여 지번 주소와 도로명 주소 정보를 얻습니다.
- **Kakao API**: `v2/local/geo/coord2address.json`
- **Example**:
  ```bash
  curl -G "http://localhost:8080/geo/coord2address" \
    --data-urlencode "x=127.423084873712" \
    --data-urlencode "y=37.0789561558879"
  ```

### 5. 좌표 → 행정구역정보 변환

- **Endpoint**: `/geo/coord2regioncode`
- **Description**: 좌표를 이용하여 행정동 및 법정동 정보를 얻습니다.
- **Kakao API**: `v2/local/geo/coord2regioncode.json`
- **Example**:
  ```bash
  curl -G "http://localhost:8080/geo/coord2regioncode" \
    --data-urlencode "x=127.1086228" \
    --data-urlencode "y=37.4012191"
  ```

### 6. 좌표계 변환

- **Endpoint**: `/geo/transcoord`
- **Description**: 서로 다른 좌표계의 좌표를 변환합니다.
- **Kakao API**: `v2/local/geo/transcoord.json`
- **Example**:
  ```bash
  curl -G "http://localhost:8080/geo/transcoord" \
    --data-urlencode "x=160710.37729270622" \
    --data-urlencode "y=-4388.879299157299" \
    --data-urlencode "input_coord=WTM" \
    --data-urlencode "output_coord=WGS84"
  ```