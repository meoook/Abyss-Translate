import React, { useState, useContext, useEffect } from "react"
import { BrowserRouter, Route, Switch, Redirect } from "react-router-dom"

import AppContext from "./context/application/appContext"

import MenuMain from "./Elems/AppComponents/MenuMain"
import Header from "./Elems/AppComponents/Header"
import PageProfile from "./Elems/PageProfile/PageProfile"
import PageTranslateFile from "./Elems/PageTranslate/PageTranslateFile"
import PageTranslateRoot from "./Elems/PageTranslate/PageTranslateRoot"
import PageAddPrj from "./Elems/PageAddPrj/PageAddPrj"
import PageProject from "./Elems/PageProject/PageProject"
import PageLogin from "./Elems/PageAccount/PageLogin"
import PageRegister from "./Elems/PageAccount/PageRegister"
import LoaderCar from "./Elems/AppComponents/LoaderCar"

// CARE - THIS CLASS HAVE 3 COMPONENTS INSIDE

const NavRouter = (props) => {
  return (
    <BrowserRouter>
      <Switch>
        <PrivateRoute exact path={"/"} component={PageProfile} />
        <PrivateRoute path={"/translates/:id"} component={PageTranslateFile} />
        <PrivateRoute path={"/translates"} component={PageTranslateRoot} />
        <PrivateRoute path={"/prj/add"} component={PageAddPrj} />
        <PrivateRoute path={"/prj/:id"} component={PageProject} />
        <Route path={"/reg"} component={PageRegister} />
        <Route path={"/login"} component={PageLogin} />
        <PrivateRoute component={NoMatchPage} />
      </Switch>
    </BrowserRouter>
  )
}

export default NavRouter

const PrivateRoute = ({ component: Component, ...rest }) => {
  const { user, accCheck } = useContext(AppContext)
  const [menuOpened, setMenuOpened] = useState(true)
  console.log("user:", user)

  useEffect(() => {
    accCheck()
    // eslint-disable-next-line
  }, [])

  return (
    <Route
      {...rest}
      render={(props) =>
        user.id ? (
          <React.Fragment>
            <MenuMain closed={!menuOpened} changeOpen={setMenuOpened} />
            <div className={`container ${menuOpened ? "small" : ""}`}>
              <Header />
              <Component {...props} />
            </div>
          </React.Fragment>
        ) : user.token ? (
          <LoaderCar />
        ) : (
          <Redirect to={{ pathname: "/login", state: { from: props.location } }} />
        )
      }
    />
  )
}

const NoMatchPage = (props) => {
  return (
    <div className='container-fluid'>
      <h1>404 URL NOT FOUND</h1>
    </div>
  )
}