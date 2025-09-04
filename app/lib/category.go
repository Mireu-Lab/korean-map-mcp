package lib

import (
	"net/http"
)

// CategoryHandler: 카테고리로 장소 검색
func (h *ApiHandler) CategoryHandler(w http.ResponseWriter, r *http.Request) {
	h.ProxyKakaoRequestStream(w, r, "/v2/local/search/category.json")
}
