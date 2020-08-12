import React from "react"
import { IcoLang, IcoLangMap } from "../icons"
import ContentProjectRoot from "./ContentProjectRoot"
import ContentProjectStart from "./ContentProjectStart"

const ContentAriaProject = ({ project, languages }) => {
  const orig = languages.find((arrItem) => arrItem.id === project.lang_orig)

  return (
    <div className='col col-10'>
      <h1 className='m-2 mh-2'>{project.name}</h1>
      <hr />
      <div className='row'>
        <div className='col col-7'>
          <div className='explorer-scroll mh-2'>
            {!project.folders_set.length ? <ContentProjectStart /> : <ContentProjectRoot />}
          </div>
        </div>
        <div className='col'>
          <div className='explorer-scroll mh-1'>
            <table className='stats'>
              <tbody>
                <tr>
                  <td>Буквы для иконки</td>
                  <td>{project.icon_chars}</td>
                </tr>
                {orig ? (
                  <tr>
                    <td>Язык оригиналов</td>
                    <td>
                      <i>
                        <IcoLang language={orig.name} />
                      </i>
                      {orig.short_name}
                    </td>
                  </tr>
                ) : (
                  <></>
                )}
                <tr>
                  <td>Необходимый перевод</td>
                  <td>
                    {project.translate_to.length ? <IcoLangMap mapLanguages={project.translate_to} /> : <>не указан</>}
                  </td>
                </tr>
                <tr>
                  <td>Создано папок</td>
                  <td>{project.folders_set.filter(() => true).length}</td>
                </tr>
                <tr>
                  <td>Файлов во всех папках</td>
                  <td>23 (fake)</td>
                </tr>
                <tr>
                  <td>Слов во всех папках</td>
                  <td>25632 (fake)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContentAriaProject
