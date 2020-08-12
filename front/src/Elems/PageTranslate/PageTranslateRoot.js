import React, { useContext, useState } from "react"

import AppContext from "../../context/application/appContext"
import Paginator from "../AppComponents/Paginator"
import LanguageSelector from "../AppComponents/LanguageSelector"

const PageTranslateRoot = (props) => {
  const { addMsg, downloadFile } = useContext(AppContext)
  const createNewMsg = () => {
    addMsg({ text: "xoxoxo xoxoxo", type: "error" })
  }
  // const [value, setValue] = useState("xaxaxaxa")

  const createNewMsg1 = () => {
    addMsg({ title: "xaxa", type: "warning" })
  }
  const createNewMsg2 = () => {
    addMsg({ title: "xaxa", text: "xoxoxo x xa axxa xasx a xas xa sxa xa xasx aa xoxoxo", type: "success" })
  }
  const createNewMsg3 = () => {
    addMsg({
      title: "xaxa",
      text: "xoxoxo x xa axxa xasx a xas xa sxa xa xasx aa xoxoxo",
      type: "success",
      nofade: true,
    })
  }
  const [selected, setSelected] = useState(72)

  const [page, setPage] = useState(1)
  const [size, setSize] = useState(25)
  const refreshPage = (pageNumber, pageSize) => {
    setPage(pageNumber)
    setSize(pageSize)
  }
  return (
    <div className='container-fluid'>
      <h1>Page Test</h1>
      <hr />
      <div className='row'>
        <button onClick={createNewMsg}>TEST</button>
        <button onClick={createNewMsg1}>TEST1</button>
        <button onClick={createNewMsg2}>TEST2</button>
        <button onClick={createNewMsg3}>TEST3</button>
      </div>
      <div>T</div>
      <div>E</div>
      <div>S</div>
      <div>T</div>
      <LanguageSelector selected={selected} setSelected={setSelected} langArr={[14, 17, 21, 72]} />
      <Paginator page={page} size={size} total={200} refresh={refreshPage} />
      <br />
      <button onClick={downloadFile.bind(this, 61)}>DOWLOAD</button>
    </div>
  )
}

export default PageTranslateRoot
