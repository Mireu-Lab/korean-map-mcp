package lib

import "net/http"

// ### 1. 주소로 좌표 변환
//
// 주소 정보를 이용해 좌표를 얻는 API입니다.
func (h *ApiHandler) AddressHandler(w http.ResponseWriter, r *http.Request) {
	h.ProxyKakaoRequestStream(w, r, "/v2/local/search/address.json")
}
