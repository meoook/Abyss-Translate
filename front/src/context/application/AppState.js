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
  EXPLORER_LOADING,
  EXPLORER_REFRESH,
  TRANSLATE_PAGE_REFRESH,
  TRANSLATE_PAGE_LOADING,
  TRANSLATE_FILE_INFO,
  TRANSLATE_CHANGE,
} from "../actionTypes"

import { nullState, connectErrMsg, findPrjByFolderID } from "../utils"

const URL = process.env.REACT_APP_API_URL

const AppState = ({ children }) => {
  const initialState = { ...nullState, token: localStorage.getItem("token") || null }
  const [state, dispatch] = useReducer(appReducer, initialState)

  const token = localStorage.getItem("token")
  const config = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Token ${state.token || token}`,
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
      console.log("REG DATA", res.data)
      accLogin({ username: username, password: password })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка регистрации"))
    }
  }
  // PROJECTS: Projects and folders lists
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
  const prjRemove = async (id) => {
    try {
      await axios.delete(`${URL}/prj/${id}/`, config)
      dispatch({ type: USER_PROJECT_REMOVE, payload: id })
    } catch (err) {
      addMsg(connectErrMsg(err, "Ошибка при удалении проекта"))
    }
  }
  const folderAdd = async (folder) => {
    try {
      const res = await axios.post(`${URL}/prj/folder/`, folder, config)
      const payload = state.projects.map((prj) => {
        if (prj.save_id !== folder.project) return prj
        return { ...prj, folders_set: [...prj.folders_set, res.data] }
      })
      dispatch({ type: USER_PROJECT_REFRESH, payload })
      return res.data.id
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу создать папку"))
    }
  }
  const folderUpdate = async (folder) => {
    try {
      const res = await axios.put(`${URL}/prj/folder/${folder.id}/`, folder, config)
      const payload = state.projects.map((prj) => {
        if (prj.save_id !== folder.project) return prj
        return {
          ...prj,
          folders_set: prj.folders_set.map((fld) => {
            if (fld.id !== folder.id) return fld
            return res.data
          }),
        }
      })
      dispatch({ type: USER_PROJECT_REFRESH, payload })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу изменить папку"))
    }
  }
  const folderRemove = async (id, prjIn) => {
    try {
      await axios.delete(`${URL}/prj/folder/${id}/`, {
        ...config,
        data: { project: prjIn },
      })
      const payload = state.projects.map((prj) => {
        if (prj.save_id !== prjIn) return prj
        return {
          ...prj,
          folders_set: prj.folders_set.filter((fldr) => fldr.id !== id),
        }
      })
      dispatch({ type: USER_PROJECT_REFRESH, payload })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу удалить папку"))
    }
  }
  // UPLOAD FILE
  const uploadFile = async (folderID, file, setProgress) => {
    const fPrj = findPrjByFolderID(folderID, state.projects)
    // const fPrj = state.projects.find((proj) => proj.folders_set.find((fold) => fold.id === folderID))
    if (!fPrj) throw new Error(`Project not found for this folder ${folderID}`)

    let formData = new FormData()
    formData.append("data", file)
    formData.append("name", file.name)
    formData.append("folder", folderID)
    if (fPrj.lang_orig) formData.append("lang_orig", fPrj.lang_orig)
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

  // FIXME: atributes as f, p, s - need to be removed from state.explorer
  // PROJECTS: File explorer
  const explorerLoading = (loadState) => dispatch({ type: EXPLORER_LOADING, payload: loadState })
  const explorerList = async (f = state.explorer.f, p = state.explorer.p, s = state.explorer.s) => {
    if (!f)
      return addMsg({
        title: "Ошибка обращения",
        text: "папка не указана в запросе",
      })
    explorerLoading()
    try {
      const res = await axios.get(`${URL}/file?f=${f}&p=${p}&s=${s}`, config)
      dispatch({ type: EXPLORER_REFRESH, payload: { ...res.data, f, p, s } })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу получить список файлов"))
    }
    // explorerLoading(false)
  }
  // TRANSLATES
  const transLoading = (loadState) => dispatch({ type: TRANSLATE_PAGE_LOADING, payload: loadState })
  const transFileInfo = async (fID, page, size, same, noTrans) => {
    transLoading()
    try {
      const res = await axios.get(`${URL}/file/${fID}`, config)
      dispatch({ type: TRANSLATE_FILE_INFO, payload: { ...res.data } })
      await transMarkList(fID, page, size, same, noTrans)
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу получить файл"))
    }
  }
  const transMarkList = async (f, p, s, d, nt) => {
    if (!f) return
    transLoading()
    try {
      const res = await axios.get(`${URL}/marks?f=${f}&p=${p}&s=${s}&d=${d}&nt=${nt}`, config)
      dispatch({ type: TRANSLATE_PAGE_REFRESH, payload: { ...res.data } })
    } catch (err) {
      addMsg(connectErrMsg(err, "Не могу получить текст файла"))
    }
  }
  const transChange = async (markID, langID, text, md5 = "") => {
    const fileID = state.translates.id
    try {
      const res = await axios.post(`${URL}/marks/`, { fileID, markID, langID, text, md5 }, config)
      const payload = state.translates.results.map((transItem) => {
        if (transItem.md5sum !== md5) return transItem
        const haveTransBefore = transItem.translates_set.find((item) => item.language === langID)
        if (!haveTransBefore)
          return {
            ...transItem,
            translates_set: [...transItem.translates_set, res.data],
          }
        const newTransSet = transItem.translates_set.map((item) => {
          if (item.language !== langID) return item
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
        user: state,
        msgs: state.msgs,
        languages: state.languages,
        explorer: state.explorer,
        explorerLoading: state.explorerLoading,
        translates: state.translates,
        translatesLoading: state.translatesLoading,
        accLogin,
        accCheck,
        accLogout,
        accRegister,
        prjList,
        prjAdd,
        prjUpdate,
        prjRemove,
        folderAdd,
        folderRemove,
        folderUpdate,
        explorerList,
        uploadFile,
        downloadFile,
        addMsg,
        delMsg,
        fetchLang,
        transFileInfo,
        transMarkList,
        transChange,
      }}>
      {children}
    </AppContext.Provider>
  )
}
export default AppState
