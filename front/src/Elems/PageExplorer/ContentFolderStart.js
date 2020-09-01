import React from "react"

const ContentFolderStart = (props) => {
  return (
    <div className='row mh-2'>
      <div className='col col-7'>
        <div>На текущий момент у вас нет ни одного файла</div>
        <div>Но Вы не отчаивайтесь. Новые файлы обязательно будут</div>
        <div>Для этого:</div>
        <div>1. нажми на зону справа</div>
        <div>2. выбери нужные для перевода файлы</div>
        <div>3. нажми кнопку загрузить</div>
        <div>После успешной загрузки, новые файлы появятся в списке.</div>
        <div>Список (пока) отфильтрован по статусу и дате добавления</div>
        <div>&nbsp;</div>
        <div>Желаем успехов в работе</div>
        <div>&nbsp;</div>
        <div>&nbsp;</div>
        <h1 className='t-right'>Кнопка для добавления файлов ---></h1>
      </div>
      <div className='col'>&nbsp;</div>
    </div>
  )
}

export default ContentFolderStart
