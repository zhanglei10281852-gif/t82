import request from "@/utils/request";

export function getHomestayCalendar(homestayId, params) {
  return request.get(`/calendar/homestay/${homestayId}`, { params });
}
