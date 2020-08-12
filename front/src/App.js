import React from "react"

import AppState from "./context/application/AppState"

import PopupMsgs from "./Elems/AppComponents/PopupMsgs"
import NavRouter from "./NavRouter"

export default function App() {
  return (
    <AppState>
      <PopupMsgs />
      <NavRouter />
    </AppState>
  )
}
