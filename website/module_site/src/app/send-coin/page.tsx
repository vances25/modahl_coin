"use client";

import styles from "./style.module.scss";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Send_Coin() {
  const router = useRouter();
  const [sender, setSender] = useState("");
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [passcode, setPasscode] = useState("");
  const [message, setMessage] = useState("");

  const sendCoin = async () => {

    if(sender == ""){
      setMessage("please filll in inputs")
      return
    }
    if(receiver == ""){
      setMessage("please filll in inputs")
      return
    }
    if(amount == ""){
      setMessage("please filll in inputs")
      return
    }
    if(passcode == ""){
      setMessage("please filll in inputs")
      return
    }


    try{
      const response = await fetch("https://172-236-101-245.ip.linodeusercontent.com/api/send_coin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sender, receiver, amount, passcode }),
      });

      const data = await response.json();
      if(data.status == "REDIRECT"){
        router.push(`/sent?wallet=${data.receiver}&amount=${data.amount}`)
        setMessage("")
      }else{
        setMessage(typeof data.message === "string" ? data.message : JSON.stringify(data))
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
      <h1 className={styles.title}>SEND COIN NOW!</h1>
      <p className={styles.subtitle}>
        Please note you can use your username or public key for sending and receiving transactions
      </p>
      <div className={styles.form_container}>
        <div className={styles.form_group}>
          <label>SENDER:</label>
          <input type="text" placeholder="Enter sender" value={sender} onChange={(e) => setSender(e.target.value)} />
        </div>
        <div className={styles.form_group}>
          <label>RECEIVER:</label>
          <input type="text" placeholder="Enter receiver" value={receiver} onChange={(e) => setReceiver(e.target.value)} />
        </div>
        <div className={styles.form_group}>
          <label>AMOUNT:</label>
          <input type="number" placeholder="Enter amount" value={amount} onChange={(e) => setAmount(e.target.value)} />
        </div>
        <div className={styles.form_group}>
          <label>PASSCODE:</label>
          <input type="password" placeholder="Enter passcode" value={passcode} onChange={(e) => setPasscode(e.target.value)} />
        </div>
        <p>{message}</p>
        <button className={styles.send_button} onClick={sendCoin}>SEND</button>
      </div>
    </div>
  );
}
