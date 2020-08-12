import React, { useState, useContext } from "react"

import AppContext from "../../context/application/appContext"

// import UserStats from "./UserStats"
import UserOptions from "./UserOptions"
// import UserOrders from "./UserOrders"
// import UserFiles from "./UserFiles"

export default function PageProfile(props) {
  const { user } = useContext(AppContext)

  const [leftSubPage, setLeftSubPage] = useState("orders")
  const handleChangeLeftSubPage = (event) => {
    if (event.target.value !== leftSubPage) setLeftSubPage(event.target.value)
  }

  const [rightSubPage, setRightSubPage] = useState("stats")
  const handleChangeRightSubPage = (event) => {
    if (event.target.value !== rightSubPage) setRightSubPage(event.target.value)
  }

  return (
    <div className='container-fluid row'>
      <div className='col col-6'>
        <h1>Profile Page</h1>
        <hr />
        <div className='row'>
          <button
            value='orders'
            className={`underline ${leftSubPage === "orders" && "active"}`}
            onClick={handleChangeLeftSubPage}>
            My Orders
          </button>
          <button
            value='files'
            className={`underline ${leftSubPage === "files" && "active"}`}
            onClick={handleChangeLeftSubPage}>
            My Files
          </button>
        </div>
        {/* {leftSubPage === "orders" && <UserOrders orders={user.translateOrders} />}
        {leftSubPage === "files" && <UserFiles files={user.files} openLoadFiles={handleChangeRightSubPage} />} */}
        <hr />
      </div>
      <div className='col col-5 offset-1'>
        <div className='row'>
          <button
            value='stats'
            className={`underline ${rightSubPage === "stats" && "active"}`}
            onClick={handleChangeRightSubPage}>
            Stats
          </button>
          <button
            value='options'
            className={`underline ${rightSubPage === "options" && "active"}`}
            onClick={handleChangeRightSubPage}>
            Options
          </button>
        </div>
        <hr />
        {/* {rightSubPage === "stats" && <UserStats stats={user.stats} />} */}
        {rightSubPage === "options" && <UserOptions options={user.options} />}
        <hr />
      </div>
    </div>
  )
}
