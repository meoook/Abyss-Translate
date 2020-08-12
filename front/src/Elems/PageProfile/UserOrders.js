import React from "react"

export default function UserOrders({ orders }) {
  return (
    <div>
      <h1>Заказы на перевод</h1>
      <div className='shadow-box'>
        <table className='table-sbd'>
          <thead>
            <tr>
              <td>&nbsp;</td>
              <td>Order start</td>
              <td>Order end</td>
              <td>Filename</td>
              <td>Total words</td>
              <td>Words translated</td>
              <td>Words left</td>
            </tr>
          </thead>
          <tbody>
            {orders.map((order, index) => {
              return (
                <tr key={order.id}>
                  <td>{index + 1}</td>
                  <td>{order.timeStart}</td>
                  <td>{order.timeEnd}</td>
                  <td>{order.filename}</td>
                  <td>{order.wordsTotal}</td>
                  <td>{order.wordsTranslated}</td>
                  <td>{order.wordsLeft}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
