import React, { useContext, useEffect, useState } from "react"
import AppContext from "../../context/application/appContext"
import InputSearchField from "../AppComponents/InputSearchField"

const PermissionsAddMenu = ({ accName, prjID }) => {
  const { permissions, permAdd, permRemove, usersList } = useContext(AppContext)
  const [name, setName] = useState("")
  const [input, setInput] = useState("")
  const [perms, setPerms] = useState([])
  const [options, setOptions] = useState([])

  const LEN_TO_SEARCH = 3

  useEffect(() => {
    if (accName) {
      setName(accName)
      setInput(accName)
      const userPerms = permissions.find((item) => item.username === accName)
      if (userPerms) setPerms(userPerms.prj_perms.map((item) => item.permission))
      else setPerms([])
    } else {
      setName("")
      setInput("")
    }
    setOptions([])
  }, [accName, permissions])

  const changeInput = (value) => {
    const searchVal = value.trim()
    console.log("ROOT: CHECK NEW INPUT", searchVal)
    // TODO: Fix change perms
    if (!searchVal) {
      console.log("ROOT: RESET")
      setName("")
      setOptions([])
      setPerms([])
    } else if (options.find((item) => item.toLowerCase() === searchVal.toLowerCase())) {
      console.log("ROOT: FOUND", permissions)
      setName(searchVal)
      const userPerms = permissions.find((item) => item.username.toLowerCase() === searchVal.toLowerCase())
      console.log("ROOT: FOUND", userPerms)
      if (userPerms) setPerms(userPerms.prj_perms.map((item) => item.permission))
      else setPerms([])
    } else if (LEN_TO_SEARCH === searchVal.length) {
      console.log("ROOT: UPDATE SEARCH")
      usersList(searchVal).then((newOptions) => {
        setOptions(newOptions.map((item) => item.username))
      })
      setName("")
      setPerms([])
    } else if (LEN_TO_SEARCH > searchVal.length) {
      console.log("ROOT: NULL SEARCH")
      setName("")
      setOptions([])
      setPerms([])
    } else {
      // setName(searchVal)
      setName("")
      setPerms([])
    }
  }

  const togglePerm = (perm) => {
    if (!name) return
    if (perms.includes(perm)) permRemove(prjID, name, perm)
    else permAdd(prjID, name, perm)
    // else permsAdd(perm, name, save_id)
  }

  return (
    <div className='scroll-y ml-2'>
      <div className='m-1'>Имя аккаунта для добавления прав</div>
      <InputSearchField val={input} setVal={changeInput} label='Имя пользователя' options={options} />
      {!name ? (
        <></>
      ) : (
        <div className='m-2'>
          <div className='box-perms link' onClick={togglePerm.bind(this, 0)}>
            <div className='col'>Переводчик</div>
            {perms.includes(0) ? (
              <div className='box-perms-toggle on'>x</div>
            ) : (
              <div className='box-perms-toggle'>-</div>
            )}
          </div>
          <div className='box-perms link'>
            <div className='col'>Приглашать переводчиков</div>
            {perms.includes(5) ? (
              <div className='box-perms-toggle on'>x</div>
            ) : (
              <div className='box-perms-toggle'>-</div>
            )}
          </div>
          <div className='box-perms link'>
            <div className='col'>Управлять файлами</div>
            {perms.includes(8) ? (
              <div className='box-perms-toggle on'>x</div>
            ) : (
              <div className='box-perms-toggle'>-</div>
            )}
          </div>
          <div className='box-perms link'>
            <div className='col'>Управлять правами</div>
            {perms.includes(9) ? (
              <div className='box-perms-toggle on'>x</div>
            ) : (
              <div className='box-perms-toggle'>-</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default PermissionsAddMenu
