import React, { useState } from "react"
import Header from "../Header"
import PageProfile from "../PageProfile"
import PageTranslate from "../PageTranslate"

export default function FrameMain({ user }) {
  const [activePage, setActivePage] = useState("profile")

  return (
    <div className='container-fluid'>
      <Header user={user} pageCurrent={activePage} pageChange={setActivePage} />
      {activePage === "profile" && <PageProfile user={user} />}
      {activePage === "translate" && <PageTranslate user={user} />}
    </div>
  )
}
