<?xml version="1.0" encoding="UTF-8"?>
<sc id="68" name="" frequency="1" steps="0" defaultIntergreenMatrix="0">
  <signaldisplays>
    <display id="1" name="Red" state="RED">
      <patterns>
        <pattern pattern="MINUS" color="#FF0000" isBold="true" />
      </patterns>
    </display>
    <display id="3" name="Green" state="GREEN">
      <patterns>
        <pattern pattern="FRAME" color="#00CC00" isBold="true" />
        <pattern pattern="SOLID" color="#00CC00" isBold="false" />
      </patterns>
    </display>
    <display id="4" name="Amber" state="AMBER">
      <patterns>
        <pattern pattern="FRAME" color="#CCCC00" isBold="true" />
        <pattern pattern="SLASH" color="#CCCC00" isBold="false" />
      </patterns>
    </display>
  </signaldisplays>
  <signalsequences>
    <signalsequence id="7" name="Red-Green-Amber">
      <state display="1" isFixedDuration="false" isClosed="true" defaultDuration="1000" />
      <state display="3" isFixedDuration="false" isClosed="false" defaultDuration="5000" />
      <state display="4" isFixedDuration="true" isClosed="true" defaultDuration="3000" />
    </signalsequence>
  </signalsequences>
  <sgs>
    <sg id="681" name="Norte" defaultSignalSequence="7" underEPICSControl="true">
      <defaultDurations>
        <defaultDuration display="1" duration="1000" />
        <defaultDuration display="3" duration="5000" />
        <defaultDuration display="4" duration="4000" />
      </defaultDurations>
      <EPICSTrafficDemands />
    </sg>
    <sg id="6823" name="Leste-Oeste" defaultSignalSequence="7" underEPICSControl="true">
      <defaultDurations>
        <defaultDuration display="1" duration="1000" />
        <defaultDuration display="3" duration="5000" />
        <defaultDuration display="4" duration="4000" />
      </defaultDurations>
      <EPICSTrafficDemands />
    </sg>
  </sgs>
  <dets />
  <messagePointPairs />
  <intergreenmatrices />
  <progs>
    <prog id="1" cycletime="128000" switchpoint="0" offset="0" intergreens="0" fitness="0.000000" vehicleCount="0" name="Plano1">
      <sgs>
        <sg sg_id="681" signal_sequence="7">
          <cmds>
            <cmd display="3" begin="77000" />
            <cmd display="1" begin="127000" />
          </cmds>
          <fixedstates>
            <fixedstate display="4" duration="4000" />
          </fixedstates>
        </sg>
        <sg sg_id="6823" signal_sequence="7">
          <cmds>
            <cmd display="3" begin="0" />
            <cmd display="1" begin="75000" />
          </cmds>
          <fixedstates>
            <fixedstate display="4" duration="4000" />
          </fixedstates>
        </sg>
      </sgs>
    </prog>
  </progs>
  <stages />
  <interstageProgs />
  <stageProgs />
  <dailyProgLists />
</sc>