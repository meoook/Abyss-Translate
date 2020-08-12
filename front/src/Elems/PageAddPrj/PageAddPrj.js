import React, { useState, useContext } from "react"

import AppContext from "../../context/application/appContext"

import PrjNameInput from "./PrjNameInput"
import PrjLanguageSelect from "./PrjLanguageSelect"
import PrjSummary from "./PrjSummary"

import { IcoGet } from "../icons"

export const PageAddPrj = (props) => {
  const { prjAdd, user, addMsg, languages } = useContext(AppContext)
  const [phase, setPhase] = useState(1)
  const titles = [
    "Шаг первый: укажите название игры",
    "Шаг второй: выбор языковых настроек",
    "Шаг третий: подтверждаем создание",
  ]
  const [project, setProject] = useState({
    name: "",
    icon_chars: "",
    lang_orig: [],
    translate_to: [],
  })
  const [shadow, setShadow] = useState({
    name: "",
    icon_chars: "",
    lang_orig: [],
    translate_to: [],
  })

  const projectFinish = () => {
    const adding = async () => {
      const toAdd = () => {
        if (project.translate_to.length) return { ...project, lang_orig: project.lang_orig[0] }
        return { name: project.name, icon_chars: project.icon_chars, lang_orig: project.lang_orig[0] }
      }
      prjAdd(toAdd()).then((prjID) => {
        props.history.push(prjID)
      })
    }
    adding()
  }

  // Components
  const BtnNext = () => {
    const onNext = () => {
      const checked = {
        name: shadow.name.trim(),
        icon_chars: shadow.icon_chars.substring(0, 2),
        lang_orig: shadow.lang_orig,
        translate_to: shadow.translate_to,
      }
      if (checked.name && checked.icon_chars.length === 2) {
        if (user.projects.find((prj) => prj.name === checked.name)) {
          addMsg({ text: "Проект с таким именем уже существует", type: "warning" })
        } else {
          setProject(checked)
          setShadow(checked)
          setPhase(phase + 1)
        }
      }
    }
    return (
      <button className='btn green' onClick={onNext}>
        Next
      </button>
    )
  }
  const BtnPrev = () => {
    const onPrev = () => {
      if (phase > 1) setPhase(phase - 1)
    }
    return (
      <button className='btn green' onClick={onPrev}>
        Prev
      </button>
    )
  }
  const BtnFinish = () => (
    <button className='btn green' onClick={projectFinish}>
      Create
    </button>
  )

  return (
    <div className='container-fluid'>
      <h1>Add project</h1>
      <hr />
      <div className='row'>
        <div className='col col-8 offset-2'>
          <div className='form'>
            <h1>облачное пространство проекта</h1>
            <div className='title'>{titles[phase - 1]}</div>
            <div className='steps row'>
              <div className='steps-line'>
                <div style={{ width: `${phase * 33.33 - 12.5}%` }}></div>
              </div>
              <div className='steps-step col col-4 active'>
                <i className='big'>
                  <IcoGet name='descr' />
                </i>
                <div>Name</div>
              </div>
              <div className={`steps-step col col-4 ${phase > 1 ? "active" : ""}`}>
                <i className='big'>
                  <IcoGet name='language' />
                </i>
                <div>Language</div>
              </div>
              <div className={`steps-step col col-4 ${phase > 2 ? "active" : ""}`}>
                <i className='big'>
                  <IcoGet name='summary' />
                </i>
                <div>Summary</div>
              </div>
            </div>
            <div className={`progress-bar ${phase > 1 ? "finish" : ""}`}>
              <div style={{ width: `${phase * 33.33}%` }}></div>
            </div>
            <div className='row justify center'>
              <h3>Создаем новый проект</h3>
              <div>Шаг {phase} из 3</div>
            </div>
            {phase === 1 && <PrjNameInput shadow={shadow} setShadow={setShadow} />}
            {phase === 2 && <PrjLanguageSelect shadow={shadow} setShadow={setShadow} />}
            {phase === 3 && <PrjSummary project={project} languages={languages} />}
            <div className='row justify center'>
              <div>{phase > 1 && <BtnPrev />}</div>
              <div>{phase < 3 ? <BtnNext /> : <BtnFinish />}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
export default PageAddPrj
