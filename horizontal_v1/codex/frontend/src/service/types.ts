export interface Pagination {
  total: number
  page: number
  size: number
}

export interface PageResult<T> {
  list: T[]
  pagination: Pagination
}
