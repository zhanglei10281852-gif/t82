import request from '@/utils/request'

export function getReviews(params) {
  return request.get('/reviews', { params })
}

export function createReview(data) {
  return request.post('/reviews', data)
}

export function getReview(id) {
  return request.get(`/reviews/${id}`)
}
