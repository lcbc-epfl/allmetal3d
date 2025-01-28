

const App = new Vue({
  el: '#app',
  components: {
    'popper': VuePopper
  },
  data: {
    title: "",
    dynamic_para: "",
    selected_items: [],
    selectionMode: "single",
    showSliderWater:true,
    showSliderMetal:true,
    config: {
      backgroundColor: "white",
      orthographic: false,
      disableFog: false,
      hoverDuration:0
    },
    settings: {
      backgroundColor: {
        type: "select",
        options: ["white", "black", "gray", "lightgray", "beige", "orange"],
      },
      orthographic: {
        type: "toggle",
      },
      disableFog: {
        type: "toggle",
      },
    },
    view: null,
    confidenceLabel: "pLDDT",
    moldata: [
      { data: "",
      name: "Input", 
      format: "pdb",
      selectable: true,
      selectionStyle: {
        "color": "greenCarbon",
        "representation": "stick",
        "multiple": true
      },
      asFrames: false,
      clickable:false},
      { data: ``, 
      name: "Output", format: "pdb", asFrames: false, clickable:true, 
      selectionStyle: {
        "color": "greenCarbon",
        "representation": "sphere",
        "multiple": false
      },
     },
    ],
    // sequence: {
    //   "A": "AAAAAAAAAA",
    //   "B": "BBBB"
    // },
    cubeData:{
      "data":"",
      "label": "Metal probability",
      "shortLabel": "p=",
    },
    cubeDataWater:{
      "data":"",
      "label": "Water probability",
      "shortLabel": "p=",
    },
    results:[
      // { 
      //   "index":1,
      //   "location_confidence":0.8,
      //   "probabilities_identity":[0.02, 0.03, 0.04, 0.05, 0.06, 0.07],
      //   "probabilities_geometry":[0,0,0,0,0,0,0],
      //   "close_residues":[
      //     {
      //       "chain":"A",
      //       "resn":"ALA",
      //       "resi":14,
      //     },
      //     {
      //       "chain":"A","resn":"ALA",
      //       "resi":17,
      //     },
      //     {
      //       "chain":"A",
      //       "resn":"ALA",
      //       "resi":1,
      //     }
      //   ]
      // },
    ],
    labelHover: true,
    hover:false,
    anyColorAlphaFold: false,
    modelAlphaFold:{},
    representations: [
      {
        model: 0,
        chain: "",
        resname: "",
        style: "cartoon",
        color: "whiteCarbon",
        residue_range: "",
        around: 0,
        byres: false,
        visible: false,
      },
      // {
      //   model: 1,
      //   chain: "",
      //   resname: "",
      //   style: "sphere",
      //   color: "whiteCarbon",
      //   residue_range: "",
      //   around: 0,
      //   byres: false,
      //   visible: false,
      // },
    ],
    selectedRepresentations: [
    ],
    selectedAtoms:[],
    showOffCanvas: false,
    showOffCanvasReps: false,
    isAnimated: false,
    selectedAtom:null,
    currentChain:"A",
    currentModel:0,
    showSequence:false,
    isovalue:0.5,
    isovalue_water:0.5,
    voldata:null,
    voldata_water:null,
    shape : null,
    shape_water:null,
    toggleRepIndex:null,
    labels:['Alkali', 'MG','CA','ZN', 'NonZNTM', 'NoMetal'],
    labels_vacancy:["Fully coordinated", "Vacancy", "NoMetal", "irregular"  ],
    labels_geometry:['tetrahedron', 'octahedron', 'pentagonal bipyramid',   'square','Irregular', 'other','NoMetal']
  },
  computed: {
    hasFrames(){
      let hF = false;
      this.moldata.forEach((element) => {
        if (element.asFrames) {
            hF= true;
        }
    });
    return hF
    },
    nModels(){
      return this.moldata.length
    },
    currentResult(){
      // find result with index
      let result = this.results.find((result) => {
        return result.index == this.selectedAtom.resi
      })
      return result
    },
    modelChains(){
      if (this.view != null){
        let chains = []
        this.view.getModel(this.currentModel).atoms.forEach((atom) => {
          if (!chains.includes(atom.chain)){
            chains.push(atom.chain)
          }
          
        })
        return chains
      }
    },
    mergedrepresentations(){
      return this.representations.concat(this.selectedRepresentations)
    },
    sequence(){
      if (this.view != null){

        let aa_map = {
          "ALA": "A",
          "ARG": "R",
          "ASN": "N",
          "ASP": "D",
          "CYS": "C",
          "GLN": "Q",
          "GLU": "E",
          "GLY": "G",
          "HIS": "H",
          "ILE": "I",
          "LEU": "L",
          "LYS": "K",
          "MET": "M",
          "PHE": "F",
          "PRO": "P",
          "SER": "S",
          "THR": "T",
          "TRP": "W",
          "TYR": "Y",
          "VAL": "V",
        }

        let seq = {}


        for (let i = 0; i < this.nModels; i++) {
          
        seq[i] = {}
        this.view.getModel(i).atoms.forEach((atom) => {
          seq[i][atom.chain] = {}
        })

        this.view.getModel(i).atoms.forEach((atom) => {
          seq[i][atom.chain][atom.resi] = atom.resn
        })
      }
        
        //use current chain to render sequence as array of 10s with mapping to single letters
        let seqArray = []
        let tempArray = []
        console.log(this.currentModel + " " + this.currentChain)
        Object.keys(seq[this.currentModel][this.currentChain]).forEach((index) => {
          residue = seq[this.currentModel][this.currentChain][index]
          let key = ""
          if (aa_map[residue] === undefined){
            key = residue
          }else{
            key = aa_map[residue]
          }
          tempArray.push({"resi":index, "resn":key})
          if (tempArray.length === 10){
            seqArray.push(tempArray)
            tempArray = []
          }
        })
        //add last array
        seqArray.push(tempArray)
        return seqArray       
        
      }
      return ""
      

    }
  },
  watch:{
    mergedrepresentations:{
      handler(newVal, oldVal){
        this.applyStyles(newVal)
        this.triggerAlphaFold()
      },
      deep:true,
    },
    isovalue:{
      handler(newVal, oldVal){
        if (this.cubeData.data !==""){

          this.view.removeShape(this.shape)
          this.shape = this.view.addIsosurface(this.voldata, { isoval:Number(newVal) , color: "orange", alpha: 0.85, smoothness: 1 });

        this.view.render();
        }
      }
    },
    isovalue_water:{
      handler(newVal, oldVal){
        if (this.cubeDataWater.data !==""){
          
          this.view.removeShape(this.shape_water)
          this.shape_water = this.view.addIsosurface(this.voldata_water, { isoval:Number(newVal) , color: "blue", alpha: 0.85, smoothness: 1 });

        this.view.render();
        }
      }
    },
    config:{
      handler(newVal, oldVal){
      this.view.setBackgroundColor(newVal.backgroundColor);
      this.view.enableFog(!newVal.disableFog);
      this.view.setCameraParameters({ orthographic: newVal.orthographic });
    },
    deep:true
    }
  },
  methods: {
    closeHighlight(){
      this.selectedAtom=null
      this.selectedRepresentations = []
      this.applyStyles(this.representations)
    },
    findMaxValue(arr) {
      console.log(arr)
      if (arr.length === 0) {
          return null; // Return null for an empty array
      }
      
      let maxValue = arr[0]; // Initialize maxValue to the first element of the array
      for (let i = 1; i < arr.length; i++) {
          if (arr[i] > maxValue) {
              maxValue = arr[i]; // Update maxValue if a larger element is found
          }
      }
      return maxValue;
  },
  findMaxValueIndex(arr) {
    console.log(arr)
      if (arr.length === 0) {
          return -1; // Return -1 for an empty array
      }
      
      let maxIndex = 0; // Initialize maxIndex to the index of the first element
      for (let i = 1; i < arr.length; i++) {
          if (arr[i] > arr[maxIndex]) {
              maxIndex = i; // Update maxIndex if a larger element is found
          }
      }
      return maxIndex;
  }, 
    isSelected(model, chain, resi){
      // if (this.selectedAtom != null){
      //   if (this.selectedAtom.resi === resi && this.selectedAtom.chain === chain && this.selectedAtom.model === model){
      //     return true
      //   }
      // }
      // return false

      //check if model, chain, resi are in selectedAtoms

      let found = false
      this.selectedAtoms.forEach((atom) => {
        if (atom.model === model && atom.chain === chain && atom.resi === resi){
          found = true
        }
      })
      return found
    },
    toggleRepresentation(model,close_residues){
      //checke what chains we have
      console.log(this.toggleRepIndex);

      if (this.toggleRepIndex == null){

      
      let chains = {}
      close_residues.forEach((residue) => {
        if (Object.keys(chains).includes(residue.chain)){
          chains[residue.chain].push(residue.resi)
        }else{
          chains[residue.chain] = [residue.resi]
        }
      })
      //check if we have a representation for each chain
      Object.keys(chains).forEach((chain) => {
        let found = false
        this.representations.forEach((representation) => {
          if (representation.chain === chain && representation.model === model && representation.residue_range === chains[chain]){
            found = true
          }
        })
        if (!found){
          // join residues using comma
          let residue_range = chains[chain].join(",")
          this.representations.push({
            "model":model,
            "chain":chain,
            "resname":"",
            "color": "whiteCarbon",
            "style": "stick",
            "residue_range":residue_range,
          "visible":false,
        "byres":false})

        this.toggleRepIndex = this.representations.length -1
        }})

      }else{
        this.deleteRep(this.toggleRepIndex);
        this.toggleRepIndex = null;
      }
      


    },
    selectAtom(model, chain, resi){
      this.selectedAtom = {"model":model, "chain":chain, "resi":resi}
      if (this.moldata[model].selectionStyle.multiple){
        //check if already selected
        let found = this.isSelected(model, chain, resi)
        if (found){
          //remove from selectedAtoms
          this.selectedAtoms = this.selectedAtoms.filter((atom) => {
            return !(atom.model === model && atom.chain === chain && atom.resi === resi)
          })
          this.selectedRepresentations = this.selectedRepresentations.filter((representation) => {
            return !(representation.model === model && representation.chain === chain && representation.residue_range === resi)
          })
        } else{

        this.selectedAtoms.push({"model":model, "chain":chain, "resi":resi})
        this.selectedRepresentations.push({
          model: model,
          chain: chain,
          resname: "",
          style: this.moldata[model].selectionStyle.representation,
          color: this.moldata[model].selectionStyle.color,
          residue_range: resi,
          around: 0,
          byres: false,
          visible: true,
      })}
      } else{
        this.selectedAtoms = [{"model":model, "chain":chain, "resi":resi}]
        this.selectedRepresentations= [{
          model: model,
          chain: chain,
          resname: "",
          style: this.moldata[model].selectionStyle.representation,
          color: this.moldata[model].selectionStyle.color,
          residue_range: resi,
          around: 0,
          byres: false,
          visible: true,
      }]
      }


      
    },
    triggerAlphaFold(){
      let anyColorAlphaFold = false;
        let MAF = {}
        this.representations.forEach((rep) => {
          if (rep.color === "alphafold") {
             anyColorAlphaFold = true
             MAF[rep.model] = true
          }else{
            if (!Object.keys(MAF).includes(rep.model)){
              MAF[rep.model] = false
            }
            
          }
        });
        this.anyColorAlphaFold = anyColorAlphaFold;
        this.modelAlphaFold = MAF
    },
    toggleAnimation() {
      if (this.isAnimated) {
        this.view.pauseAnimate();
      } else {
        this.view.animate({ loop: "forward", reps: 0 });
      }
      this.view.render();
      this.isAnimated = !this.isAnimated;
    },
    colorAlpha(atom) {
      if (atom.b < 50) {
        return "OrangeRed";
      } else if (atom.b < 70) {
        return "Gold";
      } else if (atom.b < 90) {
        return "MediumTurquoise";
      } else {
        return "Blue";
      }
    },
    deleteRep(index) {
      this.representations.splice(index, 1);
      this.applyStyles(this.representations)
     
  },
    insertRep() {
      this.representations.push({
          model: 0,
          chain: "",
          resname: "",
          style: "cartoon",
          color: "grayCarbon",
          residue_range: "",
          around: 0,
          byres: false,
          visible: true,
      })
    },
    resetZoom(rep) {
      // if is not pointerevent
      if (rep.type != undefined) {
        this.view.zoomTo();
      } else {
        let sel = {
          model: rep.model,
        };
        if (rep.chain !== "") {
          sel.chain = rep.chain;
        }
        if (rep.residue_range !== "") {
          if (typeof(rep.residue_range) === 'string'){
              
            //split based on commas
            let resis = rep.residue_range
            resis = resis.split(",")
            sel.resi = resis;
          }else{
            sel.resi = rep.residue_range;
          }

          sel.resi = rep.residue_range;
        }
        if (rep.resname !== "") {
          sel.resn = rep.resname;
        }
        this.view.zoomTo(sel);
      }
    },
    applyStyles(representations) {
      if (this.view !== undefined) {
        this.view.setStyle();
        this.view.removeAllSurfaces();
        representations.forEach((rep) => {
          let colorObj;

          if (rep.color === "alphafold") {
            colorObj = { colorfunc: this.colorAlpha };
          } else if (rep.color == "spectrum") {
            colorObj = { color: "spectrum" };
          } else {
            colorObj = { colorscheme: rep.color };
          }
          let selObj = { model: rep.model };
          if (rep.chain !== "") {
            selObj.chain = rep.chain;
          }
          if (rep.residue_range !== "") {
            // if is a string containing commas
            
            if (typeof(rep.residue_range) === 'string'){
              
              //split based on commas
              let resis = rep.residue_range
              resis = resis.split(",")
              selObj.resi = resis;
            }else{
              selObj.resi = rep.residue_range;
            }
            

          }
          if (rep.resname !== "") {
            selObj.resn = rep.resname;
          }
          selObj.byres = rep.byres;
          if (rep.around !== 0) {
            selObj.expand = rep.around;
          }
          if (rep.sidechain) {
            selObj = {
              and: [selObj, { atom: ["N", "C", "O"], invert: true }],
            };
          }
         console.log(selObj)
          if (rep.style === "surface") {
            colorObj.opacity = 0.8;
            this.view.addSurface($3Dmol.SurfaceType.VDW, colorObj, selObj);
          }else if (rep.style === "sphere"){
            this.view.addStyle(selObj, {
              "sphere": {'color': rep.color.replace("Carbon", "")},
            });
          }else {
            this.view.addStyle(selObj, {
              [rep.style]: colorObj,
            });
          }
        
        });

        this.view.render();
      }
    }
  },
  mounted() {
    // const ds = new DragSelect({
    //   selectables: document.querySelectorAll('.item-selectable'),
    //   area: document.getElementById('selectable'),
    //   draggability: false
    // });

    // ds.subscribe('callback', (e) => {
    //   this.selected_items = []
    //   e.items.map((item) => {
    //     this.selected_items.push({ "id": item.dataset.index, "chain": item.dataset.chain })
    //   })
    // });
    let pdb = document.getElementById("pdb").innerHTML
    this.moldata[0].data = pdb

    let probe = document.getElementById("probe").innerHTML
    if (probe!=" "){
      this.moldata[1].data = probe
    }else{
      this.moldata.pop()
    }    

    let cube = document.getElementById("cube").innerHTML
    this.cubeData.data = cube

    let cube_water = document.getElementById("cube_water").innerHTML
    this.cubeDataWater.data = cube_water

    let results = document.getElementById("results").innerHTML

    this.results = JSON.parse(results)


    // let element = document.querySelector('#viewer-container');
    let startingConfig = { ...this.config, cartoonQuality: 7 };
    this.view = $3Dmol.createViewer( this.$refs.viewer, startingConfig );
    // this.view.addSphere({ center: {x:0, y:0, z:0}, radius: 10.0, color: 'green' });
    this.moldata.forEach((element,index) => {
      
        if (element.asFrames) {
            this.view.addModelsAsFrames(element.data, element.format);
        } else {
            this.view.addModel(element.data, element.format);
        }
        let that = this;
        if (element.clickable){
          //click callback
          this.view.getModel(index).setClickable({},true,function(atom,viewer,event,container) {
            that.selectedAtom = {"model":index, "chain":atom.chain, "resi":atom.resi}
        });
        }
    });

    //trigger computation which model contains plddts
    // this.representations = this.representations;
    this.applyStyles(this.representations);
    this.triggerAlphaFold();

    if (this.labelHover) {
      let that = this;
      this.view.setHoverable(
          {},
          true,
          function (atom, view, event, container) {
              if (!atom.label) {
                  let label;
                  if (that.moldata[atom.model].clickable){
                    that.hover = true;
                  }
                  
                  if (that.modelAlphaFold[atom.model]) {
                      label =
                          atom.resn +
                          ":" +
                          atom.resi +
                          ":" +
                          atom.atom +
                          " (" +
                          that.confidenceLabel +
                          " " +
                          atom.b +
                          ")";
                  }else if(atom.model==1){
                    let p = atom.pdbline.substring(54, 60)*100
                    
                    label =
                          atom.resn + ":" + atom.resi + "   p=" +p +"%";
                  }else {
                      label =
                          atom.resn + ":" + atom.resi;
                  }
                  if (that.labelHover){
                    atom.label = view.addLabel(label, {
                      position: atom,
                      backgroundColor: "#ffffff",
                      borderColor: "#dddddd",
                      fontColor: "black",
                  });
                  }
                  
                  
                  that.selectedRepresentations.push({
          model: 1,
          chain: "",
          resname: "",
          style: "sphere",
          color: "greenCarbon",
          residue_range: atom.resi,
          around: 0,
          byres: false,
          visible: true,
      })
              }
          },
          function (atom, view) {
              if (atom.label) {
                that.hover = false;
                  view.removeLabel(atom.label);
                  // view.setStyle({resi:atom.resi}, {});
                  delete atom.label;
              }
              that.selectedRepresentations.pop()
          }
      );
    };


    if (this.cubeData.data !==" "){
      
      this.voldata = new $3Dmol.VolumeData(this.cubeData.data, "cube");
      this.shape = this.view.addIsosurface(this.voldata, { isoval: 0.5 , color: "orange", alpha: 0.85, smoothness: 1 });
    }else{
      this.showSliderMetal = false
    }

    
    if (this.cubeDataWater.data !==" "){
      
      this.voldata_water = new $3Dmol.VolumeData(this.cubeDataWater.data, "cube");
      this.shape_water = this.view.addIsosurface(this.voldata_water, { isoval: 0.4 , color: "blue", alpha: 0.85, smoothness: 1 });
    }else{
      this.showSliderWater = false
    }
    
    this.view.zoomTo();
    this.view.render();
    
  }
})


