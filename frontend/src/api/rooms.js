import request from "@/utils/request";

export function getRooms(params) {
  return request.get("/rooms", { params });
}

export function getRoom(id) {
  return request.get(`/rooms/${id}`);
}

export function createRoom(data) {
  return request.post("/rooms", data);
}

export function updateRoom(id, data) {
  return request.put(`/rooms/${id}`, data);
}

export function deleteRoom(id) {
  return request.delete(`/rooms/${id}`);
}
