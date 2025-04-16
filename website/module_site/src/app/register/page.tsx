"use client";

import styles from "./style.module.scss";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Send_Coin() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [confirmPasscode, setConfirmPasscode] = useState("");
  const [passcode, setPasscode] = useState("");
  const [message, setMessage] = useState("");

  const sendCoin = async () => {

    if(username == ""){
      setMessage("please filll in inputs")
      return
    }
    if(confirmPasscode == ""){
      setMessage("please filll in inputs")
      return
    }
    if(passcode == ""){
      setMessage("please filll in inputs")
      return
    }
    if(passcode != confirmPasscode){
      setMessage("passcodes do not match")
      return
    }


    try{
      const response = await fetch("https://172-236-101-245.ip.linodeusercontent.com/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, passcode }),
      });

      const data = await response.json();
      if(data.status == "OK"){
        router.push(`/welcome?key=${data.key}&username=${username}`)
        setMessage("")
      }else{
        setMessage(data.status)
      }
    }catch{
      setMessage("Error!")
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.navbar}>
        <img onClick={() => router.push("/")} src="/logo.png" alt="logo" className={styles.logo} />
      </div>
      <h1 className={styles.title}>REGISTER NOW</h1>
      <p className={styles.subtitle}>
        Through this option, we associate your private key with a passcode so you dont have to worry about managing it!
      </p>
      <div className={styles.form_container}>
        <div className={styles.form_group}>
          <label>USERNAME:</label>
          <input type="text" placeholder="Enter new username" value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div className={styles.form_group}>
          <label>PASSCODE:</label>
          <input type="password" placeholder="Enter new passcode" value={passcode} onChange={(e) => setPasscode(e.target.value)} />
        </div>
        <div className={styles.form_group}>
          <label>CONFIRM:</label>
          <input type="password" placeholder="Confirm passcode" value={confirmPasscode} onChange={(e) => setConfirmPasscode(e.target.value)} />
        </div>
        <p>{message}</p>
        <button className={styles.send_button} onClick={sendCoin}>SEND</button>
      </div>
    </div>
  );
}
