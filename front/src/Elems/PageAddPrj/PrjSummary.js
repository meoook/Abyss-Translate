import React from "react"
import { IcoLang, IcoLangMap } from "../icons"

export const PrjSummary = ({ project, languages }) => {
  const orig = languages.find((arrItem) => arrItem.id === project.lang_orig[0])
  return (
    <>
      <div className='steps-step'>Настройки можно будет поменять в процессе работы</div>
      <table className='stats'>
        <tbody>
          <tr>
            <td>Project name</td>
            <td>{project.name}</td>
          </tr>
          <tr>
            <td>Project short name</td>
            <td>{project.icon_chars}</td>
          </tr>
          {orig ? (
            <tr>
              <td>Language original</td>
              <td>
                <IcoLang language={orig.id} />
              </td>
            </tr>
          ) : (
            <></>
          )}
          {project.translate_to.length ? (
            <tr>
              <td>Languages to translate</td>
              <td>
                <IcoLangMap mapLanguages={project.translate_to} />
              </td>
            </tr>
          ) : (
            <></>
          )}
        </tbody>
      </table>
    </>
  )
}
export default PrjSummary
