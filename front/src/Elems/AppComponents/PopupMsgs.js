import React, { useContext, useEffect } from "react"
import { IcoMsg } from "../icons"
import AppContext from "../../context/application/appContext"

const PopupMsgs = () => {
  const { msgs, delMsg } = useContext(AppContext)
  return (
    <div className='msg-frame'>
      {msgs.map((msg) => (
        <Message msg={msg} delMsg={delMsg} key={msg.id} />
      ))}
    </div>
  )
}

export default PopupMsgs

const Message = ({ msg, delMsg }) => {
  const msgStyle = `${msg.type || "info"}${msg.nofade ? "" : " fade"}`

  useEffect(() => {
    if (!msg.nofade) {
      setTimeout(() => {
        delMsg(msg.id)
      }, 4500)
    }
    // eslint-disable-next-line
  }, [])
  return (
    <div className={`msg-item ${msgStyle} row center`}>
      <div className='row center'>
        <i>
          <IcoMsg type={msg.type} />
        </i>
        <div>
          {msg.title && <h3>{msg.title}</h3>}
          {msg.text && <div>{msg.text}</div>}
        </div>
        <button className='btn-close' onClick={delMsg.bind(this, msg.id)}>
          &times;
        </button>
      </div>
      <div className='msg-progress' />
    </div>
  )
}
