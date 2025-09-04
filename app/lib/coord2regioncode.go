package lib

import "net/http"

// ### 2. 좌표로 행정구역정보 변환
//
// 좌표를 이용해 행정동 및 법정동 정보를 얻는 API입니다.
func (h *ApiHandler) Coord2RegionCodeHandler(w http.ResponseWriter, r *http.Request) {
	h.ProxyKakaoRequest(w, r, "/v2/local/geo/coord2regioncode.json")
}
