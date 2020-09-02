import React, { useState, useEffect } from "react"
import Loader from "../AppComponents/Loader"

const VariantGoogle = ({ markID }) => {
  const [loading, setLoading] = useState(false)
  const [text, setText] = useState(null)

  useEffect(() => {
    if (markID) {
      setText(null)
      setLoading(true)
      setTimeout(() => {
        setText(MOCK_DATA_GOOGLE.text + markID)
        // setText("")
        setLoading(false)
      }, 3000)
    }
  }, [markID])

  return (
    <>
      {loading ? (
        <Loader />
      ) : !text ? (
        <></>
      ) : (
        <div className='card-translate m-1'>
          <div className='card-translate-head'>Google translate</div>
          <div className='card-translate-content'>{text}</div>
        </div>
      )}
    </>
  )
}

export default VariantGoogle

const MOCK_DATA_GOOGLE = { text: "some text from google translate" }
const MOCK_DATA_SERVER = [
  { id: 1, mark_id: 12, text: "some text from google translate" },
  { id: 2, mark_id: 44, text: "some text from google translate" },
]
