// import React, { Component } from "react";
// import { render } from "react-dom";
// import HomePage from "./HomePage";
// import { Button, Grid, Typography, TextField, FormControl, FormHelperText, Radio, RadioGroup, FormControlLabel } from '@mui/material';
// import { Routes, Navigate } from 'react-router-dom';



// export default class App extends Component {
//   constructor(props) {
//     super(props);
//   }

//   render() {
//     return (
//       <div className="center">
//         <HomePage />
//       </div>
//     );
//   }
// }

// const appDiv = document.getElementById("app");
// render(<App />, appDiv);




import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from "./HomePage";
import CreateRoomPage from "./CreateRoomPage"; // Import your CreateRoomPage
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Typography, TextField, FormHelperText, FormControl, Radio, FormControlLabel } from '@mui/material';

export default class App extends Component {
  render() {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create" element={<CreateRoomPage />} />
        </Routes>
      </Router>
    );
  }
}

const appDiv = document.getElementById("app");
render(<App />, appDiv);
