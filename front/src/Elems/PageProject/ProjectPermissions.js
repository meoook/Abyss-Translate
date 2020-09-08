import React, { useContext, useEffect, useState } from "react"
import AppContext from "../../context/application/appContext"
import Loader from "../AppComponents/Loader"
import PermissionsAddMenu from "./PermissionsAddMenu"

const ProjectPermissions = ({ prjID }) => {
  const { permissions, permList } = useContext(AppContext)
  const [loading, setLoading] = useState(true)
  const [accName, setAccName] = useState(null)

  useEffect(() => {
    if (prjID) {
      setLoading(true)
      setAccName(null)
      permList(prjID).then(() => {
        setLoading(false)
      })
    }
    // eslint-disable-next-line
  }, [prjID])

  return (
    <div className='expl row mt-2'>
      <div className='col col-7 column'>
        <div className='table-head'>
          <div className='col col-4'>Имя</div>
          <div className='col col-2'>trans</div>
          <div className='col col-2'>invite</div>
          <div className='col col-2'>manage</div>
          <div className='col col-2'>admin</div>
        </div>
        <div className='scroll-y'>
          {loading ? (
            <Loader />
          ) : !permissions.length ? (
            <h3 className='m-2 mh-3'>&nbsp;Права никому не выданы</h3>
          ) : (
            <div>
              {permissions.map((item) => (
                <PermissionItem key={item.username} perm={item} setAcc={setAccName} />
              ))}
            </div>
          )}
        </div>
      </div>
      <div className='col col-5 column'>
        <div className='table-head ml-2'>Выдача прав пользователям</div>
        <PermissionsAddMenu accName={accName} prjID={prjID} />
      </div>
    </div>
  )
}

export default ProjectPermissions

const PermissionItem = ({ perm, setAcc }) => {
  return (
    <div className='table-line link m-1' onClick={setAcc.bind(this, perm.username)}>
      <div className='col col-4'>{perm.username}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 0) && "x"}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 5) && "x"}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 8) && "x"}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 9) && "x"}</div>
    </div>
  )
}
