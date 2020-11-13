import React, { useContext, useEffect, useState } from "react"
import AppContext from "../../context/application/appContext"
import { displayStringDate } from "../componentUtils"

const MarkChangeLog = ({ mark, fileID }) => {
  const { transLog } = useContext(AppContext)
  const [logMsgs, setLogMsgs] = useState([])

  useEffect(() => {
    transLog(fileID, mark).then((data) => {
      setLogMsgs(data)
    })
  }, [mark, fileID, transLog])

  return (
    <div className='MarkChangeLog'>
      <h3 className='mt-3'>Последние изменения для ID: {mark}</h3>
      <hr />
      {logMsgs.map((item) => (
        <div key={item.created}>
          <span className='color-white mr-0'>
            {displayStringDate(item.created)} {item.user}
          </span>
          <span>{item.text}</span>
        </div>
      ))}
    </div>
  )
}

export default MarkChangeLog
