import React, { useContext, useEffect, useState } from "react"
import AppContext from "../../context/application/appContext"
import InputMultiField from "../AppComponents/InputMultiField"

const PermissionsAddMenu = ({ accName }) => {
  const { permissions, permsAdd, permsRemove } = useContext(AppContext)
  const [name, setName] = useState("")
  const [perms, setPerms] = useState([])
  const [options, setOptions] = useState([
    { id: 1, name: "aaaaa" },
    { id: 2, name: "bbbbb" },
    { id: 3, name: "1qaz" },
  ])

  useEffect(() => {
    if (accName) {
      setName(accName)
      const userPerms = permissions.find((item) => item.username === accName)
      if (userPerms) setPerms(userPerms.prj_perms.map((item) => item.permission))
      else setPerms([])
    } else setName("")
  }, [accName, permissions])

  const changeName = (event) => {
    setName(event.target.value)
  }
  const selectName = (values) => {
    setOptions(values)
    const name = values[0]
    const userPerms = permissions.find((item) => item.username === name)
    setName(name) // set new name
    if (userPerms) setPerms(userPerms.prj_perms.map((item) => item.permission))
    else setPerms([])
  }

  return (
    <div className='scroll-y ml-2'>
      <div className='m-1'>Имя аккаунта для добавления прав</div>
      <div>
        <input type='text' value={name} onChange={changeName} placeholder='имя пользователя' />
      </div>
      <div>
        <InputMultiField values={[3]} options={options} setValues={selectName} />
      </div>
      {!name ? (
        <></>
      ) : (
        <div className='m-2'>
          <div className='box-perms link'>
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
