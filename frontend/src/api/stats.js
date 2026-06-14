import request from "@/utils/request";

export function getHomestayRevenue(homestayId, params) {
  return request.get(`/stats/revenue/homestay/${homestayId}`, { params });
}

export function getDashboardStats(params) {
  return request.get("/stats/dashboard", { params });
}

export function getHomestayRanking() {
  return request.get("/stats/homestay-ranking");
}
