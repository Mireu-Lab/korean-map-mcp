package lib

import "net/http"

// ### 3. 좌표로 주소 변환
//
// 좌표를 이용해 지번 주소와 도로명 주소 정보를 얻는 API입니다.
func (h *ApiHandler) Coord2AddressHandler(w http.ResponseWriter, r *http.Request) {
	h.ProxyKakaoRequest(w, r, "/v2/local/geo/coord2address.json")
}
