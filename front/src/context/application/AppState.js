import React, { useReducer } from "react"
import axios from "axios"
import { AppContext } from "./appContext"
import { appReducer } from "./appReducer"
import {
  POPUP_MESSAGE_ADD,
  POPUP_MESSAGE_REMOVE,
  LANGUAGES_REFRESH,
  INIT_LOADER,
  USER_ACC_VALID,
  USER_ACC_LOGOUT,
  USER_PROJECT_REFRESH,
  USER_PROJECT_REMOVE,
  USER_PROJECT_ADD,
  EXPLORER_REFRESH,
  TRANSLATE_PAGE_REFRESH,
  TRANSLATE_PAGE_LOADING,
  TRANSLATE_FILE_INFO,
  TRANSLATE_CHANGE,
  PRJ_FOLDER_REFRESH,
  PRJ_FOLDER_ADD,
  PRJ_FOLDER_REMOVE,
} from "../actionTypes"

import { nullState, connectErrMsg, findPrjByFolderID } from "../utils"

const URL = process.env.REACT_APP_API_URL

const AppState = ({ children }) => {
  const initialState = { ...nullState, user: { token: localStorage.getItem("token") || null } }
  const [state, dispatch] = useReducer(appReducer, initialState)

  const token = localStorage.getItem("token") // TODO: походу лишнее
  const config = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Token ${state.user.token || token}`,
    },
  }

  const loading = (loadState) => dispatch({ type: INIT_LOADER, payload: loadState })
  const addMsg = (msg) => dispatch({ type: POPUP_MESSAGE_ADD, payload: msg })
  const delMsg = (id) => dispatch({ type: POPUP_MESSAGE_REMOVE, payload: +id })

  // INIT
  const fetchLang = async () => {
    try {
      const res = await axios.get(`${URL}/lang/`, config)
      dispatch({ type: LANGUAGES_REFRESH, payload: res.data })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка получения списка язков"))
    }
  }
  // ACCOUNT
  const accCheck = async () => {
    loading()
    if (state.id) return
    if (!token) return dispatch({ type: USER_ACC_LOGOUT })
    await axios
      .get(`${URL}/auth/user`, config)
      .then((res) => {
        dispatch({ type: USER_ACC_VALID, payload: res.data })
      })
      .catch((err) => {
        if (err.response) {
          dispatch({ type: USER_ACC_LOGOUT }) // go to login page
          localStorage.removeItem("token")
        } else {
          addMsg({
            title: "Сервер недоступен",
            text: "Ошибкa подключения",
            type: "error",
            nofade: true,
          })
        }
      })
  }
  const accLogin = async (credentials) => {
    loading()
    await axios
      .post(`${URL}/auth/login`, credentials)
      .then((res) => {
        localStorage.setItem("token", res.data.token)
        dispatch({
          type: USER_ACC_VALID,
          payload: { ...res.data.user, token: res.data.token },
        })
      })
      .catch((err) => {
        dispatch({ type: USER_ACC_LOGOUT })
        addMsg(connectErrMsg(err, "Неверное сочетание логина и пароля"))
      })
  }
  const accLogout = async () => {
    localStorage.removeItem("token")
    dispatch({ type: USER_ACC_LOGOUT })
    await axios.post(`${URL}/auth/logout`, null, config).catch((err) => {
      addMsg(connectErrMsg(err, "Ошибка выхода"))
    })
  }
  const accRegister = async ({ username, email, password }) => {
    try {
      const res = await axios.post(`${URL}/auth/register`, { username, email, password })
      accLogin({ username: username, password: password })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка регистрации"))
    }
  }
  // PROJECTS
  const prjList = async () => {
    loading()
    try {
      const res = await axios.get(`${URL}/prj/`, config)
      dispatch({ type: USER_PROJECT_REFRESH, payload: res.data })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка получения списка проектов"))
    }
  }
  const prjAdd = async (project) => {
    try {
      const res = await axios.post(`${URL}/prj/`, project, config)
      dispatch({ type: USER_PROJECT_ADD, payload: res.data })
      return res.data.save_id
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу создать проект"))
    }
  }
  const prjUpdate = async (project) => {
    try {
      const res = await axios.put(`${URL}/prj/${project.save_id}/`, project, config)
      const payload = state.projects.map((prj) => {
        if (prj.save_id !== res.data.save_id) return prj
        else return res.data
      })
      dispatch({ type: USER_PROJECT_REFRESH, payload })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка при изменении проекта"))
    }
  }
  const prjRemove = async (save_id) => {
    try {
      await axios.delete(`${URL}/prj/${save_id}/`, config)
      dispatch({ type: USER_PROJECT_REMOVE, payload: save_id })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка при удалении проекта"))
    }
  }
  // FOLDERS
  const fldrList = async (save_id) => {
    try {
      const res = await axios.get(`${URL}/prj/folder/`, { ...config, params: { save_id } })
      dispatch({ type: PRJ_FOLDER_REFRESH, payload: res.data })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка получения списка папок"))
    }
  }
  const fldrAdd = async (folder) => {
    try {
      const res = await axios.post(`${URL}/prj/folder/`, folder, config)
      dispatch({ type: PRJ_FOLDER_ADD, payload: res.data })
      return res.data.id
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу создать папку"))
    }
  }
  const fldrUpdate = async (folder) => {
    try {
      const res = await axios.put(`${URL}/prj/folder/${folder.id}/`, folder, config)
      const payload = state.folders.map((fldr) => {
        return fldr.id !== res.data.id ? fldr : res.data
      })
      dispatch({ type: PRJ_FOLDER_REFRESH, payload })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу изменить папку"))
    }
  }
  const fldrRemove = async (folder_id) => {
    try {
      await axios.delete(`${URL}/prj/folder/${folder_id}/`, config)
      dispatch({ type: PRJ_FOLDER_REMOVE, payload: folder_id })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу удалить папку"))
    }
  }
  // UPLOAD & DOWNLOAD FILE
  const uploadFile = async (folderID, file, setProgress) => {
    let formData = new FormData()
    formData.append("data", file)
    formData.append("name", file.name)
    formData.append("folder_id", folderID)
    try {
      await axios.post(`${URL}/transfer/`, formData, {
        headers: { ...config.headers },
        onUploadProgress: (progressEvent) => {
          setProgress({
            [file.name]: Math.round((progressEvent.loaded / progressEvent.total) * 100),
          })
        },
      })
    } catch (err) {
      addMsg(connectErrMsg(err, `Не удалось загрузить файл ${file.name}`))
      throw new Error(`Не удалось загрузить файл ${file.name}`)
    }
  }
  const downloadFile = async (translatedID, filename) => {
    // if (!filename) filename = state.explorer.find()
    console.log('XXXXXXXX', translatedID, filename)
    try {
      // FIXME: Axios can't get Content-Disposition - filename
      const res = await axios.get(`${URL}/transfer/${translatedID}`, config)
      const obj_url = window.URL.createObjectURL(new Blob([res.data]))
      let tmp_elem = document.createElement("a")
      tmp_elem.href = obj_url
      tmp_elem.setAttribute("download", filename)
      document.body.appendChild(tmp_elem)
      tmp_elem.click()
      tmp_elem.remove()
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу скачать файл"))
    }
  }
  // PROJECTS: File explorer
  const explList = async (save_id, folder_id, page, size) => {
    if (!save_id && !folder_id) {
      dispatch({ type: EXPLORER_REFRESH, payload: {} })
    } else {
      try {
        const res = await axios.get(`${URL}/file`, {
          ...config,
          params: { save_id, folder_id, page, size },
        })
        dispatch({ type: EXPLORER_REFRESH, payload: res.data })
        addMsg({ text: "Получен список файлов", type: "success" })
      } catch (err) {
        addMsg(connectErrMsg(err, "Не могу получить список файлов"))
      }
    }
  }
  // TRANSLATES
  const transFileInfo = async (fID, page, size, same, noTrans) => {
    try {
      const res = await axios.get(`${URL}/file/${fID}`, config)
      dispatch({ type: TRANSLATE_FILE_INFO, payload: { ...res.data } })
      await transList(fID, page, size, same, noTrans)
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу получить файл"))
    }
  }
  const transList = async (file_id, page, size, distinct, no_trans) => {
    try {
      const res = await axios.get(`${URL}/marks`, {
        ...config,
        params: { file_id, page, size, distinct, no_trans },
      })
      dispatch({ type: TRANSLATE_PAGE_REFRESH, payload: res.data })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу получить текст файла"))
    }
  }
  const transChange = async (mark_id, lang_id, text, md5 = "") => {
    const file_id = state.translates.id
    try {
      const res = await axios.post(`${URL}/marks/`, { file_id, mark_id, lang_id, text, md5 }, config)
      const payload = state.translates.results.map((transItem) => {
        if (transItem.md5sum !== md5) return transItem
        const haveTransBefore = transItem.translates_set.find((item) => item.language === lang_id)
        if (!haveTransBefore)
          return {
            ...transItem,
            translates_set: [...transItem.translates_set, res.data],
          }
        const newTransSet = transItem.translates_set.map((item) => {
          if (item.language !== lang_id) return item
          return res.data
        })
        return { ...transItem, translates_set: newTransSet }
      })
      dispatch({ type: TRANSLATE_CHANGE, payload })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу получить текст файла"))
    }
  }

  return (
    <AppContext.Provider
      value={{
        // state,
        loading: state.loading,
        msgs: state.msgs,
        user: state.user,
        languages: state.languages,
        projects: state.projects,
        folders: state.folders,
        explorer: state.explorer,
        translates: state.translates,
        addMsg,
        delMsg,
        fetchLang,
        accLogin,
        accCheck,
        accLogout,
        accRegister,
        prjList,
        prjAdd,
        prjUpdate,
        prjRemove,
        fldrList,
        fldrAdd,
        fldrRemove,
        fldrUpdate,
        explList,
        uploadFile,
        downloadFile,
        transFileInfo,
        transMarkList: transList,
        transChange,
      }}>
      {children}
    </AppContext.Provider>
  )
}
export default AppState
