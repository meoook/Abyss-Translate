import React from "react"

export const PrjRepositoriesList = ({ shadow, setShadow }) => {
  const gitUrlRemove = (url) => {
    setShadow({ ...shadow, repositories: shadow.repositories.filter((el) => el !== url) })
  }

  return (
    <div className='urls'>
      {shadow.repositories.map((repo) => (
        <div key={repo} className='input-group row m-2'>
          <div className='input-like'>https://{repo}</div>
          <button
            className='btn red'
            onClick={() => {
              gitUrlRemove(repo)
            }}>
            &times;
          </button>
        </div>
      ))}
    </div>
  )
}
export default PrjRepositoriesList
