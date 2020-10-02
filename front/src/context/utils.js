// CONSTANTS
export const nullState = {
  loading: false,
  user: { id: null, token: null, role: null, username: null, email: null },
  msgs: [],
  languages: [],
  projects: [],
  permissions: [],
  folders: [],
  explorer: {},
  translates: {},
  repository: {},
}

// FUNCTIONS
// For: AppState -> MsgID
export const getNextId = (arr) => {
  if (arr.length === 0) return 0
  else return arr[arr.length - 1].id + 1
}
// For: API Answers
export const connectErrMsg = (err, msg, title = "") => {
  if (!err.response) return { text: "Сервер недоступен", type: "warning" }
  console.warn("Err from UserState:", err.response.statusText) // TODO: Обработка ошибок - вывод err.response.data
  return { text: msg, type: "warning", title }
}
