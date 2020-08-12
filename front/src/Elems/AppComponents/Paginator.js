import React, { useState, useEffect } from "react"

const Paginator = ({ page, size, total, refresh }) => {
  // UTILS
  const PAG_WIDTH = 3 // Total = [<][1][2][3][X][5][6][7][>]
  const getPages = (pageNumber, size, total) => {
    const pagesAmount = Math.ceil(total / size)
    const result = []
    let start = pageNumber - PAG_WIDTH
    if (start <= 1) start = 1
    else result.push("<<")
    const end = pageNumber + PAG_WIDTH
    if (end >= pagesAmount) {
      for (let index = start; index < pagesAmount + 1; index++) {
        result.push(index)
      }
    } else {
      for (let index = start; index < end + 1; index++) {
        result.push(index)
      }
      result.push(">>")
    }
    return result
  }

  const [pages, setPages] = useState(getPages(page, size, total))

  useEffect(() => {
    setPages(getPages(page, size, total))
  }, [page, size, total])

  const handleClick = (event) => {
    if (event.target.name === "size") refresh(page, size >= 100 ? 25 : size * 2)
    else {
      switch (event.target.value) {
        case "<<": // &lt;&lt;
          refresh(page - PAG_WIDTH - 1, size)
          break
        case ">>": // &gt;&gt;
          refresh(page + PAG_WIDTH + 1, size)
          break
        default:
          refresh(+event.target.value, size)
      }
    }
  }

  return (
    <>
      {pages.length > 1 && (
        <div className='fix-bot'>
          <div className='paginator'>
            <div className='col col-6'>
              {pages.map((pageItem) => (
                <button
                  key={pageItem}
                  className={`btn btn-icon gray${page === pageItem ? " active" : ""}`}
                  value={pageItem}
                  onClick={handleClick}>
                  {pageItem}
                </button>
              ))}
            </div>
            <div className='col col-2'>
              <button className='btn btn-icon gray' name='size' onClick={handleClick}>
                {size}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default Paginator
