import React from "react"

const Toggler = ({ val, setVal }) => {
  return (
    <div className={`toggler${val ? " toggled" : ""}`} onClick={setVal.bind(this, !val)}>
      <span className='toggler-circle'></span>
    </div>
  )
}

export default Toggler
