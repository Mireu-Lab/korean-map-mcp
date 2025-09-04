제공된 Kakao Developers 로컬 API 문서를 기반으로 `CURL`을 사용하여 요청할 수 있는 모든 방식은 다음과 같습니다. 각 API는 HTTP GET 메서드를 사용하며, 인증을 위해 REST API 키를 헤더에 포함해야 합니다.

**참고:** 아래의 모든 예제에서 `${REST_API_KEY}` 부분은 본인의 카카오 REST API 키로 대체해야 합니다.

### 1. 주소로 좌표 변환

주소 정보를 이용해 좌표를 얻는 API입니다.

```bash
curl -v -G GET "https://dapi.kakao.com/v2/local/search/address.json" \
  -H "Authorization: KakaoAK ${REST_API_KEY}" \
  --data-urlencode "query=전북 삼성동 100"
```

### 2. 좌표로 행정구역정보 변환

좌표를 이용해 행정동 및 법정동 정보를 얻는 API입니다.

```bash
curl -v -G GET "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json" \
  -H "Authorization: KakaoAK ${REST_API_KEY}" \
  --data-urlencode "x=127.1086228" \
  --data-urlencode "y=37.4012191"
```

### 3. 좌표로 주소 변환

좌표를 이용해 지번 주소와 도로명 주소 정보를 얻는 API입니다.

```bash
curl -v -G GET "https://dapi.kakao.com/v2/local/geo/coord2address.json" \
  -H "Authorization: KakaoAK ${REST_API_KEY}" \
  --data-urlencode "x=127.423084873712" \
  --data-urlencode "y=37.0789561558879" \
  --data-urlencode "input_coord=WGS84"
```

### 4. 좌표계 변환

서로 다른 좌표계의 좌표를 변환하는 API입니다.

```bash
curl -v -G GET "https://dapi.kakao.com/v2/local/geo/transcoord.json" \
  -H "Authorization: KakaoAK ${REST_API_KEY}" \
  --data-urlencode "x=160710.37729270622" \
  --data-urlencode "y=-4388.879299157299" \
  --data-urlencode "input_coord=WTM" \
  --data-urlencode "output_coord=WGS84"
```

### 5. 키워드로 장소 검색

특정 키워드로 장소를 검색하는 API입니다. 중심 좌표와 반경을 지정하여 검색할 수도 있습니다.

```bash
curl -v -G GET "https://dapi.kakao.com/v2/local/search/keyword.json" \
  -H "Authorization: KakaoAK ${REST_API_KEY}" \
  --data-urlencode "query=카카오프렌즈" \
  --data-urlencode "y=37.514322572335935" \
  --data-urlencode "x=127.06283102249932" \
  --data-urlencode "radius=20000"
```

### 6. 카테고리로 장소 검색

미리 정의된 카테고리 코드를 이용해 장소를 검색하는 API입니다.

```bash
curl -v -G GET "https://dapi.kakao.com/v2/local/search/category.json" \
  -H "Authorization: KakaoAK ${REST_API_KEY}" \
  --data-urlencode "category_group_code=PM9" \
  --data-urlencode "radius=20000" \
  --data-urlencode "x=127.06283102249932" \
  --data-urlencode "y=37.514322572335935"
```