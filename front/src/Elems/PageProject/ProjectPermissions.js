import React, { useContext, useEffect, useState } from "react"
import AppContext from "../../context/application/appContext"
import Loader from "../AppComponents/Loader"

const ProjectPermissions = ({ prjID }) => {
  const { permissions, permList, permAdd, permRemove } = useContext(AppContext)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    console.log("GETTINNG PERMISSSIONS COMP")
    if (prjID) {
      setLoading(true)
      permList(prjID).then(() => {
        setLoading(false)
      })
    }
  }, [prjID])

  return (
    <div className='expl row mt-2'>
      <div className='col col-7 column'>
        {/* <div className='table-head'>
          <span>Список прав пользователей</span>
          <span className='color-error t-vsmall ml-1'>&nbsp;(в стадии разработки)</span>
        </div> */}
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
                <PermissionItem key={item.username} perm={item} />
              ))}
            </div>
          )}
        </div>
      </div>
      <div className='col col-5 column'>
        <div className='table-head ml-2'>
          <span>Выдача прав пользователям</span>
          <span className='color-error t-vsmall ml-1'>&nbsp;(в стадии разработки)</span>
        </div>
        <div className='scroll-y ml-2'>
          <div className='m-2'>Add menu</div>
        </div>
      </div>
    </div>
  )
}

export default ProjectPermissions

const PermissionItem = ({ perm }) => {
  return (
    <div className='table-line m-1'>
      <div className='col col-4'>{perm.username}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 0) && "x"}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 5) && "x"}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 8) && "x"}</div>
      <div className='col col-2'>{perm.prj_perms.find((item) => item.permission === 9) && "x"}</div>
    </div>
  )
}
