import React, { useState, useEffect } from "react"
import Loader from "../AppComponents/Loader"

const MOCK_DATA_GOOGLE = { text: "Some text from google translate" }

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
      }, 1200)
    }
  }, [markID])

  return (
    <>
      {loading ? (
        <div className='m-2'><Loader /></div>
      ) : !text ? (
        <></>
      ) : (
        <div className='card-translate m-1'>
          <div className='card-translate-head'>Google translate</div>
          <div className='card-translate-content m-1 mb-3'>{text}</div>
        </div>
      )}
    </>
  )
}

export default VariantGoogle

