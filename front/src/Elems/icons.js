import React, { useContext } from "react"
import AppContext from "../context/application/appContext"
// App icons
import { ReactComponent as SvgSearch } from "../IMG/search.svg"
import { ReactComponent as SvgLanguage } from "../IMG/language.svg"
import { ReactComponent as SvgFolder } from "../IMG/folder.svg"
import { ReactComponent as SvgFolderOut } from "../IMG/folder_out.svg"
import { ReactComponent as SvgDescr } from "../IMG/description.svg"
import { ReactComponent as SvgCloudIn } from "../IMG/backup.svg"
import { ReactComponent as SvgSummary } from "../IMG/storage.svg"
import { ReactComponent as SvgWork } from "../IMG/work.svg"
import { ReactComponent as SvgWorkOut } from "../IMG/work_out.svg"
import { ReactComponent as SvgArrows } from "../IMG/arrows.svg"
// Lang icons
import { ReactComponent as SvgWorld } from "../IMG/lang/world.svg"
import { ReactComponent as SvgRussian } from "../IMG/lang/russian.svg"
import { ReactComponent as SvgEnglish } from "../IMG/lang/english.svg"
import { ReactComponent as SvgGerman } from "../IMG/lang/german.svg"
import { ReactComponent as SvgChinese } from "../IMG/lang/chinese.svg"
import { ReactComponent as SvgSpanish } from "../IMG/lang/spanish.svg"
// Message icons
import { ReactComponent as SvgInfo } from "../IMG/notification.svg"
import { ReactComponent as SvgSuccess } from "../IMG/success.svg"
import { ReactComponent as SvgWarning } from "../IMG/warning.svg"
import { ReactComponent as SvgError } from "../IMG/error.svg"

export const IcoMsg = ({ type }) => {
  switch (type) {
    case "success":
      return <SvgSuccess />
    case "warning":
      return <SvgWarning />
    case "error":
      return <SvgError />
    default:
      return <SvgInfo />
  }
}
export const IcoGet = ({ name }) => {
  switch (name.toLowerCase()) {
    case "arrows":
      return <SvgArrows />
    case "cloudin":
      return <SvgCloudIn />
    case "descr":
      return <SvgDescr />
    case "folder":
      return <SvgFolder />
    case "foldero":
      return <SvgFolderOut />
    case "language":
      return <SvgLanguage />
    case "search":
      return <SvgSearch />
    case "summary":
      return <SvgSummary />
    case "work":
      return <SvgWork />
    case "worko":
      return <SvgWorkOut />
    default:
      return <></>
  }
}
export const IcoLang = ({ language = "" }) => {
  switch (language.toLowerCase()) {
    case "german":
      return <SvgGerman />
    case "english":
      return <SvgEnglish />
    case "spanish":
      return <SvgSpanish />
    case "russian":
      return <SvgRussian />
    case "chinese":
      return <SvgChinese />
    default:
      return <SvgWorld />
  }
}
export const IcoLangMap = ({ mapLanguages = [] }) => {
  const { languages } = useContext(AppContext)
  const searchItem = (item) => languages.find((lang) => lang.id === item)
  return (
    <div className='row'>
      {mapLanguages.map((item) => (
        <div key={item} className='pr-1'>
          <i className='bd'>
            <IcoLang language={searchItem(item).name} />
          </i>
          {searchItem(item).short_name}
        </div>
      ))}
    </div>
  )
}
