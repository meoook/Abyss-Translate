import {
  INIT_LOADER,
  LANGUAGES_REFRESH,
  POPUP_MESSAGE_ADD,
  POPUP_MESSAGE_REMOVE,
  USER_PROJECT_ADD,
  USER_PROJECT_REMOVE,
  USER_PROJECT_REFRESH,
  USER_ACC_VALID,
  USER_ACC_LOGOUT,
  EXPLORER_LOADING,
  EXPLORER_REFRESH,
  TRANSLATE_PAGE_LOADING,
  TRANSLATE_PAGE_REFRESH,
  TRANSLATE_FILE_INFO,
  TRANSLATE_CHANGE,
} from "../actionTypes"

import { getNextId, nullState } from "../utils"

const handlers = {
  [INIT_LOADER]: (state, { payload = true }) => ({ ...state, loading: payload }),
  [LANGUAGES_REFRESH]: (state, { payload }) => ({ ...state, languages: payload, loading: false }),
  [USER_ACC_VALID]: (state, { payload }) => ({ ...state, ...payload, loading: false }),
  [USER_ACC_LOGOUT]: (state) => ({ ...nullState }),
  [USER_PROJECT_REFRESH]: (state, { payload }) => ({ ...state, projects: payload, loading: false }),
  [USER_PROJECT_ADD]: (state, { payload }) => ({ ...state, projects: [...state.projects, payload], loading: false }),
  [USER_PROJECT_REMOVE]: (state, { payload }) => ({
    ...state,
    projects: state.projects.filter((prj) => prj.save_id !== payload),
  }),
  [POPUP_MESSAGE_ADD]: (state, { payload }) => ({
    ...state,
    msgs: [...state.msgs, { id: getNextId(state.msgs), ...payload }],
  }),
  [POPUP_MESSAGE_REMOVE]: (state, { payload }) => ({
    ...state,
    msgs: state.msgs.filter((msg) => msg.id !== payload),
  }),
  [EXPLORER_LOADING]: (state, { payload = true }) => ({ ...state, explorerLoading: payload }),
  [EXPLORER_REFRESH]: (state, { payload }) => ({ ...state, explorer: payload, explorerLoading: false }),
  [TRANSLATE_PAGE_LOADING]: (state, { payload = true }) => ({ ...state, translatesLoading: payload }),
  [TRANSLATE_PAGE_REFRESH]: (state, { payload }) => ({
    ...state,
    translates: { ...state.translates, ...payload },
    translatesLoading: false,
  }),
  [TRANSLATE_FILE_INFO]: (state, { payload }) => ({ ...state, translates: payload }),
  [TRANSLATE_CHANGE]: (state, { payload }) => ({ ...state, translates: { ...state.translates, results: payload } }),
  DEFAULT: (state) => state,
}

export const appReducer = (state, action) => {
  const handler = handlers[action.type] || handlers.DEFAULT
  return handler(state, action)
}
