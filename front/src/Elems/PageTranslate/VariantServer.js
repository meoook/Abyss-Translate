import React, { useState, useEffect } from "react"
import Loader from "../AppComponents/Loader"

const MOCK_DATA_SERVER = [
  { id: 1, mark_id: 12, text: "Этот текст уже переведен в файле и похож на этот" },
  { id: 2, mark_id: 44, text: "Какой то похожий текст переведенный" },
]

const VariantGoogle = ({ markID }) => {
  const [loading, setLoading] = useState(false)
  const [srvData, setSrvData] = useState([])

  useEffect(() => {
    if (markID) {
      setSrvData(null)
      setLoading(true)
      setTimeout(() => {
        setSrvData(MOCK_DATA_SERVER)
        // setText("")
        setLoading(false)
      }, 600)
    }
  }, [markID])

  return (
    <>
      {loading ? (
        <div className='m-2'><Loader /></div>
      ) : !srvData.length ? (
        <></>
      ) : (
        <div className='card-translate m-1'>
          <div className='card-translate-head'>Похожие из файла</div>
          <div className='card-translate-content'>
            {srvData.map((item) => (
              <div key={item.id} className='m-1'>
                <div className='row justify'>
                  <div>ID {item.mark_id}</div>
                  <div>trID {item.id}</div>
                </div>
                <hr />
                <div className='mb-3'>{item.text}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

export default VariantGoogle

