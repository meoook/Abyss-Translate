import React, { useContext, useState, useEffect } from "react"
import AppContext from "../../context/application/appContext"

import InputMultiField from "../AppComponents/InputMultiField"

export const PrjLanguageSelect = ({ shadow, setShadow }) => {
  const { languages } = useContext(AppContext)
  const [transSelect, setTransSelect] = useState(languages.filter((item) => item.id !== shadow.lang_orig[0]))

  useEffect(() => {
    setTransSelect(languages.filter((item) => item.id !== shadow.lang_orig[0]))
  }, [shadow, languages])

  const changeOrig = (values) => {
    setShadow({
      ...shadow,
      lang_orig: values,
      translate_to: shadow.translate_to.filter((item) => item !== values[0]),
    })
  }
  const changeTrans = (values) => {
    setShadow({ ...shadow, translate_to: values })
  }

  return (
    <React.Fragment>
      <div className='steps-step'>
        При добавлении новых файлов, будут использоваться языковые настройки указанные ниже
      </div>
      <div className='row'>
        <div className='col col-10 offset-1 shadow-box'>
          <div className='mb-2'>Укажи язык с которого надо будет переводить оригинальные файлы *</div>
          <div>
            <InputMultiField values={shadow.lang_orig} setValues={changeOrig} options={languages} />
          </div>
        </div>
      </div>
      <div className='row'>
        <div className='col col-10 offset-1 shadow-box'>
          <div className='mb-2'>Укажи язык на который необходимо будет переводить оригиналы *</div>
          <InputMultiField values={shadow.translate_to} setValues={changeTrans} options={transSelect} isMulti={true} />
        </div>
      </div>
      <div className='steps-step'>
        В случае необходимости языковые настройки можно будет указать для каждого файла отдельно
      </div>
      <div className='steps-step'>* языковые настройки не являются обязательными</div>
    </React.Fragment>
  )
}
export default PrjLanguageSelect
