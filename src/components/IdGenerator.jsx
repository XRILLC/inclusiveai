import React from "react";
import stringHash from "string-hash";

class IdGenerator extends React.Component {
  constructor(props) {
    super(props);
    this.timeout = 1000;
    this.defaultId = "???";
    this.state = {
      netId: null,
      psuedoAnonId: this.defaultId  
    }
    this.secret = "ling-582-fa-2024";
    this.handleChange = this.handleChange.bind(this);
  }

  sterilizeId(rawId) {
    return rawId.toLowerCase().replace(/\s/g, '');
  }
  
  handleChange(event) {
    let netId = this.sterilizeId(event.target.value);
    this.setState({ 
      netId: netId,
      psuedoAnonId: (netId.length > 0  && netId !== this.defaultId) ? stringHash(`${this.secret}-${netId}`) : this.defaultId
    });  
  }

  render() {
    return (
      <div class="css-1ccrm8j">
        <br></br>
        <table class="css-1ccrm8j-Table">
          <tr>
              <td>
                <span><label><b>NetId</b>:</label> </span>
              </td>
              <td>             
                <input 
                  autoFocus
                  type="textarea"
                  autoComplete="off"
                  placeholder="???"
                  name="netId" 
                  onChange={this.handleChange}
                  class="css-1ccrm8j"
                />
              </td>
          </tr>
          <tr>
            <td>
            <span><label><b>Pseudonym</b>:</label> </span>
            </td>
            <td>
              <span>{this.state.psuedoAnonId}</span>
            </td>
          </tr>
          </table>
          <br></br>
      </div>
    )
  }
}

export default IdGenerator;