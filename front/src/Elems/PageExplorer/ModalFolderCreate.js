import React, { useState } from "react"

const ModalFolderCreate = ({ closeModal, folderAdd }) => {
  const [folderTitle, setFolderTitle] = useState("")
  const onChange = (event) => {
    setFolderTitle(event.target.value)
  }

  const doNothing = (event) => {
    // event.preventDefault()
    event.stopPropagation()
  }

  return (
    <div className='modal' onClick={closeModal}>
      <div className='modal-content shadow-box' onClick={doNothing}>
        <h1>Создать папку проекта</h1>
        <div className='btn-close' onClick={closeModal}>
          &times;
        </div>
        <div>Введи название папки</div>
        <input type='text' className='m-2' onChange={onChange} autoFocus={true} />
        <div className='row justify'>
          <div></div>
          <div>
            <button className='btn green' onClick={folderAdd.bind(this, folderTitle)}>
              Create
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ModalFolderCreate
