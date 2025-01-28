
import json

def html_molecule(pdb_content, probe, results,cube,water_cube, public_link):
    print(results)
    return """
<!DOCTYPE html>
<html lang="en">

<head>

    <script src="https://duerrsimon.github.io/allmetal3d/_static/vue.js"></script>
    <script src="https://unpkg.com/dragselect@latest/dist/ds.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.3/3Dmol.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/popper.js@1.14.6/dist/umd/popper.js"></script>
    <script src="https://unpkg.com/vue-popperjs/dist/vue-popper.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/vue-popperjs/dist/vue-popper.css">

    <title>VUE 3d</title>

    <style>
        .item {
            width: 50px;
            height: 50px;
            color: red;
            border: 0;
        }

        .item:focus {
            border: 1px solid rbg(0, 155, 255);
        }

        .ds-selected {
            outline: 3px solid black;
            outline-offset: 3px;
            color: black;
            font-weight: bold;
        }
        .sequence_container {
    overflow-wrap: anywhere;
    counter-reset: sequence;
}
.sequence_container .sequence__chunk {
    display: inline-block;
    margin: 1rem 0 1rem 1rem;
    /* width: 10ch; */
    position: relative;
    white-space: nowrap;
}
.sequence_container .sequence__chunk:not(:last-child):before, .sequence_container .sequence__chunk--display-last:before {
    content: counter(sequence);
    counter-increment: sequence 10;
    position: absolute;
    top: -0.8em;
    right: 0;
    opacity: .5;
    font-weight: bold;
}
.sequence-container .sequence__chunk::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    transform-origin: left;
    transform: scaleX(0.1);
    box-shadow: var(--box-shadow);
}
.sequence__chunk span{
    padding: 0 0.05rem;
}

.tooltip .tooltip-text{
    display: none;
}
.tooltip:hover .tooltip-text{
    display: block;
}
    </style>
</head>

<body>

    <textarea style="display:none" id="pdb">"""+pdb_content+""" </textarea>
    <textarea style="display:none" id="probe">"""+probe+""" </textarea>
    <textarea style="display:none" id="results">"""+json.dumps(results)+"""</textarea>
    <textarea style="display:none" id="cube">"""+cube+""" </textarea>
    <textarea style="display:none" id="cube_water">"""+water_cube+""" </textarea>


  <div id="app">

        <div class="flex">
            <!-- <div class="w-1/3">
                <div class=" px-4 border border-gray-200 shadow border-gray-200 rounded-xl  mt-10" id="selectable">
                    <div class="flex items-center justify-between border-b dark:border-gray-600">

                        <div class="flex flex-wrap items-center divide-gray-200 sm:divide-x dark:divide-gray-600">
                            <div class="flex items-center space-x-1 ">
                                <button type="button"
                                    class="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600 flex space-x-1 items-center"
                                    :class="selectionMode==&apos;single&apos;?&apos;bg-gray-100 dark:bg-gray-600&apos;:&apos;&apos;"
                                    @click="selectionMode=&apos;single&apos;">
                                    <svg aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"
                                        class="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zM12 2.25V4.5m5.834.166l-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243l-1.59-1.59"
                                            stroke-linecap="round" stroke-linejoin="round"></path>
                                    </svg>
                                    <span class="text-xs">Residue</span>
                                </button>
                                <button type="button"
                                    class="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600 flex space-x-1 items-center"
                                    @click="selectionMode=&apos;chain&apos;">
                                    <svg aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"
                                        class="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zM12 2.25V4.5m5.834.166l-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243l-1.59-1.59"
                                            stroke-linecap="round" stroke-linejoin="round"></path>
                                    </svg>
                                    <span class="text-xs">Chain</span>
                                </button>
                            </div>
                            <div class="flex flex-wrap items-center space-x-1 sm">
                                <button type="button"
                                    class="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600 flex space-x-1 items-center">
                                    <svg aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"
                                        viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
                                        <path
                                            d="M13.5 16.875h3.375m0 0h3.375m-3.375 0V13.5m0 3.375v3.375M6 10.5h2.25a2.25 2.25 0 002.25-2.25V6a2.25 2.25 0 00-2.25-2.25H6A2.25 2.25 0 003.75 6v2.25A2.25 2.25 0 006 10.5zm0 9.75h2.25A2.25 2.25 0 0010.5 18v-2.25a2.25 2.25 0 00-2.25-2.25H6a2.25 2.25 0 00-2.25 2.25V18A2.25 2.25 0 006 20.25zm9.75-9.75H18a2.25 2.25 0 002.25-2.25V6A2.25 2.25 0 0018 3.75h-2.25A2.25 2.25 0 0013.5 6v2.25a2.25 2.25 0 002.25 2.25z"
                                            stroke-linecap="round" stroke-linejoin="round"></path>
                                    </svg>
                                    <span class="text-xs">Insert segment</span>
                                </button>
                            </div>
                            <div class="flex flex-wrap items-center space-x-1 ">
                                <button type="button"
                                    class="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600 flex space-x-1 items-center">
                                    <svg aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"
                                        viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
                                        <path
                                            d="M12 9.75L14.25 12m0 0l2.25 2.25M14.25 12l2.25-2.25M14.25 12L12 14.25m-2.58 4.92l-6.375-6.375a1.125 1.125 0 010-1.59L9.42 4.83c.211-.211.498-.33.796-.33H19.5a2.25 2.25 0 012.25 2.25v10.5a2.25 2.25 0 01-2.25 2.25h-9.284c-.298 0-.585-.119-.796-.33z"
                                            stroke-linecap="round" stroke-linejoin="round"></path>
                                    </svg>
                                    <span class="text-xs leading-tight">Delete residues</span>
                                </button>
                            </div>
                            <div class="flex flex-wrap items-center space-x-1 ">
                                <button type="button"
                                    class="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600 flex space-x-1 items-center">
                                    <svg aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"
                                        viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
                                        <path
                                            d="M12 9.75L14.25 12m0 0l2.25 2.25M14.25 12l2.25-2.25M14.25 12L12 14.25m-2.58 4.92l-6.375-6.375a1.125 1.125 0 010-1.59L9.42 4.83c.211-.211.498-.33.796-.33H19.5a2.25 2.25 0 012.25 2.25v10.5a2.25 2.25 0 01-2.25 2.25h-9.284c-.298 0-.585-.119-.796-.33z"
                                            stroke-linecap="round" stroke-linejoin="round"></path>
                                    </svg>
                                    <span class="text-xs leading-tight">Delete residues</span>
                                </button>
                            </div>
                        </div>

                    </div>

                    <div class="w-full overflow-x-scroll p-2 ">


                        <div class="w-[780px] my-5 flex " v-for="chain in Object.keys(sequence)" :key="chain">

                            <div class="w-[60px] h-full">
                                <div class="mt-[24px] font-medium text-sm py-1">
                                    chain {{chain}}
                                </div>

                            </div>
                            <div class="w-[720px] flex flex-col relative">
                                <div class="w-full h-[24px] whitespace-nowrap flex font-mono text-gray-400">
                                    <div class="ml-2 block">1</div>
                                    <div class="ml-[1095px] block">100</div>
                                </div>
                                <div class="flex  w-full  bg-gray-100 text-sm group h-[24px]">
                                    <div class="w-[24px] h-[24px]  dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white border border-gray-300 bg-white px-2 py-1 flex items-center justify-center item-selectable cursor-pointer"
                                        :class="selectionMode===&apos;chain&apos;? &apos;group-hover:bg-gray-100 group:hover:text-gray-700&apos; : &apos;hover:bg-gray-100 hover:text-gray-700&apos;"
                                        v-for="(aa,i) in sequence[chain]" :key="chain + aa + i" :data-chain="chain"
                                        :data-index="i">
                                        <a href="#" class=" leading-tight text-gray-500 ">{{aa}}</a>
                                    </div>





                                </div>
                            </div>
                        </div>


                    </div>

                    <div class="py-2">
                        <h1 class="py-1 font-medium">Selections</h1>
                        <div class="flex flex-col text-sm">

                            <div class="bg-gray-50 p-2">
                                Sele1
                            </div>
                        </div>
                    </div>
                </div>
            </div> -->
            <div class="w-1/2">

                <div class="bg-white p-5 h-screen w-full" :class="hover ? &apos;cursor-pointer&apos;:&apos;&apos;">
                    <div class="gr-form overflow-hidden flex border-solid border gap-px rounded-lg flex-wrap">
                        <div
                            class="gr-block gr-box relative w-full overflow-hidden border-dashed border border-gray-300 border-gray-200" style="height:800px">
                            <!-- <div
                                class="absolute z-50    top-0 left-0 bg-white rounded-br border-b border-r border-gray-200 p-1">
                                <span class=" flex items-center space-x-1 text-xs text-gray-500"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"
                                        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
                                        stroke-linecap="round" stroke-linejoin="round"
                                        class="feather feather-file h-3 w-3">
                                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                                        <polyline points="13 2 13 9 20 9" />
                                    </svg> <span>Molecule3D</span>
                                </span>
                            </div> -->

                            <div
                                class="absolute z-50 top-0 right-0 mr-2 flex flex-col divide-y border border-gray-200 mt-2 rounded items-center justify-center bg-white">
                                <button class="p-2" title="Reset View" @click="resetZoom">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="1.5" stroke="currentColor"
                                        class="w-4 h-4 text-gray-500 hover:text-orange-600 cursor-pointer">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                                    </svg>
                                </button>
                                <button class="p-2" title="Settings" @click="showOffCanvas =!showOffCanvas">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="1.5" stroke="currentColor"
                                        class="w-5 h-5 text-gray-500 hover:text-orange-600 cursor-pointer">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
                                    </svg>
                                </button>

                                <button class="p-2" title="Representations"
                                    @click="showOffCanvasReps =!showOffCanvasReps">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="1.5" stroke="currentColor"
                                        class="w-5 h-5 text-gray-500 hover:text-orange-600 cursor-pointer">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M21.75 6.75a4.5 4.5 0 01-4.884 4.484c-1.076-.091-2.264.071-2.95.904l-7.152 8.684a2.548 2.548 0 11-3.586-3.586l8.684-7.152c.833-.686.995-1.874.904-2.95a4.5 4.5 0 016.336-4.486l-3.276 3.276a3.004 3.004 0 002.25 2.25l3.276-3.276c.256.565.398 1.192.398 1.852z" />
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M4.867 19.125h.008v.008h-.008v-.008z" />
                                    </svg>
                                </button>

                                <!-- <button class="p-2" title="Download files" @click="downloadFiles">
                                    <svg aria-hidden="true" fill="currentColor" viewBox="0 0 20 20"
                                        xmlns="http://www.w3.org/2000/svg"
                                        class="w-5 h-5 text-gray-500 hover:text-orange-600 cursor-pointer">
                                        <path
                                            d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z" />
                                        <path
                                            d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z" />
                                    </svg>
                                </button> -->
                            </div>


                            <div class="absolute bottom-0 left-0 z-50 p-2" v-if="anyColorAlphaFold">
                                <div class="flex text-xs items-center space-x-2">
                                    <div class="flex space-x-1 py-1 items-center">
                                        <span class="w-4 h-4"
                                            style="background-color: rgb(0, 83, 214);">&nbsp;</span><span
                                            class="legendlabel">Very high ({{confidenceLabel}} &gt; 90)</span>
                                    </div>
                                    <div class="flex space-x-1 py-1 items-center">
                                        <span class="w-4 h-4"
                                            style="background-color: rgb(101, 203, 243);">&nbsp;</span><span
                                            class="legendlabel">Confident (90 &gt; {{confidenceLabel}} &gt; 70)</span>
                                    </div>
                                    <div class="flex space-x-1 py-1 items-center">
                                        <span class="w-4 h-4"
                                            style="background-color: rgb(255, 219, 19);">&nbsp;</span><span
                                            class="legendlabel">Low (70 &gt; {{confidenceLabel}} &gt; 50)</span>
                                    </div>
                                    <div class="flex space-x-1 py-1 items-center">
                                        <span class="w-4 h-4"
                                            style="background-color: rgb(255, 125, 69);">&nbsp;</span><span
                                            class="legendlabel">Very low ({{confidenceLabel}} &lt; 50)</span>
                                    </div>
                                </div>
                            </div>



                            <div v-if="hasFrames"
                                class="absolute z-50 bottom-0 right-0 mr-2 flex divide-x border border-gray-200 mb-2 rounded items-center justify-center">

                                <button class="p-2" title="Play" @click="toggleAnimation" v-if="isAnimated">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="2" stroke="currentColor"
                                        class="w-4 h-4 text-gray-500 hover:text-orange-600 cursor-pointer">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                                    </svg>
                                </button>

                                <button class="p-2" title="Pause" @click="toggleAnimation" v-else>
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="2" stroke="currentColor"
                                        class="w-4 h-4 text-gray-500 hover:text-orange-600 cursor-pointer">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M5.25 7.5A2.25 2.25 0 017.5 5.25h9a2.25 2.25 0 012.25 2.25v9a2.25 2.25 0 01-2.25 2.25h-9a2.25 2.25 0 01-2.25-2.25v-9z" />
                                    </svg>

                                    <!-- <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke-width="2"
                                                stroke="currentColor"
                                                class="w-4 h-4 text-gray-500 hover:text-orange-600 cursor-pointer"
                                            >
                                                <path
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                    d="M15.75 5.25v13.5m-7.5-13.5v13.5"
                                                />
                                            </svg> -->
                                </button>

                            </div>

                            <div class="absolute top-0 h-28 z-20 flex flex-col  w-full font-mono  text-xs overflow-y-scroll">
                                <div class="bg-gray-100 pt-2 px-2 h-5/6 border-b" v-if="showSequence">
                                        <div class="sequence_container ">
                                        <div class="sequence__chunk" v-for="(tenAA,index) in sequence" :key="&apos;tenAA&apos;+index">
                                            <span class="p-0.1 hover:bg-green-200 cursor-pointer"
                                            :class="isSelected(currentModel, currentChain, aa.resi) ? &apos;bg-green-200&apos; : &apos;&apos;"
                                             v-for="(aa, i) in tenAA" @click="selectAtom(currentModel, currentChain, aa.resi)">{{aa.resn}}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="h-1/6 mt-2 font-sans flex justify-between">
                                  <button
                                   class="bg-white p-2 flex space-x-2 rounded  ml-2 border h-8 whitespace-nowrap">
                                    <div  @click="showSequence = !showSequence" class="flex space-x-1 border-r pr-2">
                                        <svg v-if="showSequence" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="h-4 w-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"></path>
                                          </svg>
                                        <svg v-else fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="h-4 w-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"></path>
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                          </svg>
                                          <span><span v-if="showSequence">Hide</span><span v-else>Show</span> sequence</span>
                                        
                                    </div>
                                    <div class="whitespace-nowrap">
                                        <span>Model</span>
                                        <select v-model="currentModel" class="bg-white" >
                                            <option v-for="(moldata, index) in moldata" :key="&apos;model&apos;+index" :value="index">{{index}}</option>
                                        </select>
                                    </div>
                                    <div>
                                        <select v-model="currentChain" class="bg-white">
                                            <option v-for="chain in modelChains" :key="&apos;chains&apos;+chain" :value="chain">{{chain}}</option>
                                        </select>
                                    </div>
                                    
                                  </button>

                                  <div class="w-2/3 flex flex-col">
                                    <div class="flex justify-center items-center h-10 space-x-3 pr-6" v-if="showSliderMetal">
                                    <div class="font-thin text-gray-600 flex items-center space-x-2"><span class="mt-1 w-10 pr-2">Metal p={{isovalue}}</span></div>
                                    <div class="w-2/3 h-4 text-orange-600">
                                        <label for="steps-range" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white sr-only">Range steps</label>
                                        <input id="steps-range" type="range" min="0" max="1" value="0.5" step="0.05" class="w-full h-0.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-orange-600" v-model="isovalue">
                                    </div>
                                    </div>

                                    <div class="flex justify-center items-center h-10 space-x-3 pr-6" v-if="showSliderWater">
                                    <div class="font-thin text-gray-600 flex items-center space-x-2"><span class="mt-1 w-10 pr-2">Water p={{isovalue_water}}</span></div>
                                    <div class="w-2/3 h-4 text-blue-600">
                                        <label for="steps-range-water" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white sr-only">Range steps</label>
                                        <input id="steps-range-water" type="range" min="0" max="1" value="0.5" step="0.05" class="w-full h-0.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-blue-600" v-model="isovalue_water">
                                    </div>
                                    </div>

                                  </div>
                            
                        </div>

                            </div>                          
                            
                            <div class="viewer w-full h-full z-10 mt-20 relative" ref="viewer"></div> 



                            <div id="settings-drawer"
                                class="absolute top-0 right-0 z-50 h-full overflow-y-auto transition-transform bg-gray-100  w-80 dark:bg-gray-800 border-l border-gray-100"
                                tabindex="-1" aria-labelledby="settings-drawer-label" v-if="showOffCanvas">
                                <div class="p-4">
                                    <h5 id="settings-drawer-label"
                                        class="inline-flex items-center mb-4 text-base font-semibold text-gray-500 dark:text-gray-400">
                                        Settings
                                    </h5>
                                    <button type="button" data-drawer-hide="drawer-example"
                                        aria-controls="drawer-example"
                                        class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 absolute top-2.5 right-2.5 inline-flex items-center dark:hover:bg-gray-600 dark:hover:text-white"
                                        @click="showOffCanvas = !showOffCanvas">
                                        <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"
                                            xmlns="http://www.w3.org/2000/svg">
                                            <path fill-rule="evenodd"
                                                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        <span class="sr-only">Close menu</span>
                                    </button>
                                </div>

                                <div class="flex flex-col mb-4 divide-y" v-for="setting in Object.keys(settings)"
                                    :key="setting">
                                    <div
                                        class="flex items-center border-t border-b border-gray-200 bg-white px-4 py-2 space-x-2">




                                        <label :for="setting"
                                            class="text-sm font-medium text-gray-600 dark:text-gray-400 w-1/2">
                                            {{setting}}
                                        </label>




                                        <label v-if="settings[setting].type == &apos;toggle&apos;"
                                            class="relative inline-flex items-center mr-5 cursor-pointer text-center justify-center">
                                            <input type="checkbox" value="" class="sr-only peer"
                                                v-model="config[setting]" />
                                            <div
                                                class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-focus:ring-4 peer-focus:ring-orange-300 dark:peer-focus:ring-orange-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[&apos;&apos;] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-400">
                                            </div>
                                        </label>


                                        <div class="flex items-center" v-if="settings[setting].type == &apos;range&apos;">
                                            <input id="medium-range" type="range" :min="settings[setting].min"
                                                :max="settings[setting].max" :step="settings[setting].step"
                                                v-model="config[setting]"
                                                class="w-2/3  h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" />
                                            <span
                                                class="w-1/3 text-center text-sm font-medium text-gray-600 dark:text-gray-400">{{config[setting]}}</span>
                                        </div>

                                        <select v-if="settings[setting].type == &apos;select&apos;"
                                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                            v-model="config[setting]">

                                            <option v-for="option in settings[setting].options" :value="option"
                                                :selected="option ==
                                                                    config[setting]">
                                                {{option}}
                                            </option>

                                        </select>


                                    </div>
                                </div>

                                <div class="bg-white">
                                    <div
                                        class="flex items-center border-t border-b border-gray-200 bg-white px-4 py-2 space-x-2">
                                        <label class="text-sm font-medium text-gray-600 dark:text-gray-400 w-1/2">
                                            Label atoms on hover
                                        </label>
                                        <label
                                            class="relative inline-flex items-center mr-5 cursor-pointer text-center justify-center">
                                            <input type="checkbox" class="sr-only peer" v-model="labelHover" />
                                            <div
                                                class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-focus:ring-4 peer-focus:ring-orange-300 dark:peer-focus:ring-orange-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[&apos;&apos;] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-400" > </div>
                                        </label>
                                    </div>
                                </div>
                            </div>

                      

                <div id="off-canvas-reps"
                    class="absolute top-0 right-0 z-50 h-full overflow-y-auto transition-transform bg-gray-100  w-80 dark:bg-gray-800 border-l border-gray-100"
                    tabindex="-1" aria-labelledby="off-canvas-reps-label" v-if="showOffCanvasReps">
                    <div class="p-4">
                        <h5 id="off-canvas-reps-label"
                            class="inline-flex items-center mb-4 text-base font-semibold text-gray-500 dark:text-gray-400">
                            Representations
                        </h5>
                        <button type="button" data-drawer-hide="off-canvas-reps" aria-controls="off-canvas-reps"
                            class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 absolute top-2.5 right-2.5 inline-flex items-center dark:hover:bg-gray-600 dark:hover:text-white"
                            @click="showOffCanvasReps =!showOffCanvasReps">
                            <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"
                                xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd"
                                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                    clip-rule="evenodd" />
                            </svg>
                            <span class="sr-only">Close menu</span>
                        </button>
                    </div>


                    <div v-for="(rep, index) in representations "
                        class="bg-white border-b border-t border-gray-200 py-4 px-2">

                        <div class="">
                            <div class="flex space-x-2 items-center cursor-pointer p-1">
                                <button @click="rep.visible = !rep.visible" class="flex items-center space-x-2">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="1.5" stroke="currentColor" :class="rep.visible
                                                                ? &apos;transform rotate-90 w-5 h-5&apos;
                                                                : &apos;w-5 h-5&apos;">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                                    </svg>
                                    <span>Representation #{{index}}</span>
                                </button>
                                <button @click="deleteRep(index)">
                                    <!---->
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                                    </svg>
                                </button>
                                <button title="zoom to selection" @click="resetZoom(rep)">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                        stroke-width="1.5" stroke="currentColor"
                                        class="w-4 h-4 text-gray-500 hover:text-orange-600 cursor-pointer">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                                    </svg>
                                </button>
                            </div>

                            <div v-if="rep.visible">
                                <div class="p-1 flex space-x-1">
                                    <select id="style"
                                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        v-model="rep.model">
                                        <option v-for="(mol,i) in moldata" :value="i" :key="&apos;model&apos;+i">
                                            {{mol.name}} #{{i}}</option>

                                    </select>
                                    <input type="text" id="chain"
                                        class="w-1/2 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        placeholder="Chain" v-model="rep.chain" />
                                </div>
                                <div class="p-1 flex space-x-1">
                                    <input type="text" id="chain"
                                        class="w-1/2 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        placeholder="Resname" v-model="rep.resname" />
                                    <input type="text" id="residue_range"
                                        class="w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        placeholder="Residue range" v-model="rep.residue_range" />
                                </div>
                                <div class="p-1 flex space-x-1 items-center">
                                    <label :for="&apos;style_rep&apos;+index"
                                        class="block mb-2 text-sm w-1/3 font-medium text-gray-600 dark:text-white">Select
                                        style</label>
                                    <select :id="&apos;style_rep&apos;+index"
                                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        v-model="rep.style">
                                        <option value="stick">Stick</option>
                                        <option value="cartoon">Cartoon</option>
                                        <!-- <option value="surface">Surface</option> -->
                                        <option value="sphere">Sphere</option>
                                    </select>
                                </div>
                                <div class="flex p-1 items-center text-gray-700 space-x-1 text-sm">
                                    <div class="">Expand selection</div>
                                    <input id="around" type="range" min="0" max="10" step="0.5" v-model="rep.around"
                                        class="h-2 w-1/3 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" />
                                    <input type="text" v-model="rep.around" class="w-8" />
                                    <div>Å</div>
                                </div>

                                <div class="flex p-1 items-center text-gray-700 text-sm">
                                    <div class="flex space-x-1 w-1/2 pr-2">
                                        <span class="whitespace-nowrap">Full residue</span>
                                        <label
                                            class="relative inline-flex items-center mr-5 cursor-pointer text-center h-6">
                                            <input type="checkbox" value="" class="sr-only peer" v-model="rep.byres" />
                                            <div
                                                class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-focus:ring-4 peer-focus:ring-orange-300 dark:peer-focus:ring-orange-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[&apos;&apos;] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-400" ></div>
                                        </label>
                                    </div>
                                    <div class="flex space-x-1 w-1/2">
                                        <span class="whitespace-nowrap ">Only sidechain</span>
                                        <label
                                            class="relative inline-flex items-center mr-5 cursor-pointer text-center h-6">
                                            <input type="checkbox" value="" class="sr-only peer"
                                                v-model="rep.sidechain" />
                                            <div
                                                class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-focus:ring-4 peer-focus:ring-orange-300 dark:peer-focus:ring-orange-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[&apos;&apos;] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-400">
                                            </div>
                                        </label>
                                    </div>
                                </div>

                            </div>
                        </div>
                        <div class="flex space-x-2 mt-2 w-full p-2">
                            <button
                                :class="rep.color ===
                                                                &apos;orangeCarbon&apos;
                                                                    ?&apos;bg-orange-600 rounded-full w-8 h-8 border-4 border-gray-300  cursor-pointer&apos;
                                                                    : &apos;bg-orange-600 rounded-full w-8 h-8 border-4 border-white cursor-pointer&apos;"
                                @click="rep.color =&apos;orangeCarbon&apos;" > </button>
                            <button
                                :class="rep.color ===
                                                                &apos;redCarbon&apos;
                                                                    ?&apos;bg-red-600 rounded-full w-8 h-8 border-4 border-gray-300  cursor-pointer&apos;
                                                                    : &apos;bg-red-600 rounded-full w-8 h-8 border-4 border-white cursor-pointer&apos;"
                                @click="rep.color =&apos;redCarbon&apos;" > </button>
                            <button
                                :class="rep.color ===
                                                                &apos;greenCarbon&apos;
                                                                    ?&apos;bg-green-600 rounded-full w-8 h-8 border-4 border-gray-300  cursor-pointer&apos;
                                                                    : &apos;bg-green-600 rounded-full w-8 h-8 border-4 border-white cursor-pointer&apos;"
                                @click="rep.color =&apos;greenCarbon&apos;"></button>
                            <button
                                :class="rep.color ===
                                                                &apos;blueCarbon&apos;
                                                                    ?&apos;bg-blue-600 rounded-full w-8 h-8 border-4 border-gray-300  cursor-pointer&apos;
                                                                    : &apos;bg-blue-600 rounded-full w-8 h-8 border-4 border-white cursor-pointer&apos;"
                                @click="rep.color =&apos;blueCarbon&apos;"></button>
                        </div>
                        <div class="py-2 text-sm group:m-1">
                            <button
                                :class="rep.color ===
                                                                &apos;alphafold&apos;
                                                                    ?&apos;rounded-lg p-1 border border-gray-400 cursor-pointer bg-gray-200&apos;
                                                                    : &apos;rounded-lg p-1 border border-gray-200 cursor-pointer bg-white&apos;"
                                @click="rep.color =&apos;alphafold&apos;">AlphaFold</button>
                            <button
                                :class="rep.color ===
                                                            &apos;default&apos;
                                                                ?&apos;rounded-lg p-1 border border-gray-400 cursor-pointer bg-gray-200&apos;
                                                                : &apos;rounded-lg p-1 border border-gray-200 cursor-pointer bg-white&apos;"
                                @click="rep.color =&apos;default&apos;">PyMol</button>

                            <button
                                :class="rep.color ===
                                                            &apos;jmol&apos;
                                                                ?&apos;rounded-lg p-1 border border-gray-400 cursor-pointer bg-gray-200&apos;
                                                                : &apos;rounded-lg p-1 border border-gray-200 cursor-pointer bg-white&apos;"
                                @click="rep.color =&apos;jmol&apos;">JMol</button>

                            <button
                                :class="rep.color ===
                                                        &apos;chain&apos;
                                                            ?&apos;rounded-lg p-1 border border-gray-400 cursor-pointer bg-gray-200&apos;
                                                            : &apos;rounded-lg p-1 border border-gray-200 cursor-pointer bg-white&apos;"
                                @click="rep.color =&apos;chain&apos;">chain</button>
                            <button
                                :class="rep.color ===
                                                    &apos;spectrum&apos;
                                                        ?&apos;rounded-lg p-1 border border-gray-400 cursor-pointer bg-gray-200&apos;
                                                        : &apos;rounded-lg p-1 border border-gray-200 cursor-pointer bg-white&apos;"
                                @click="rep.color =&apos;spectrum&apos;">Spectrum</button>

                        
                            </div>
                        </div>   
              
        <button
            class="w-full flex text-orange-600 justify-center my-2 text-sm space-x-2 items-center hover:text-gray-600 cursor-pointer"
            @click="insertRep">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2"
                stroke="currentColor" class="w-4 h-4">
                <path stroke-linecap="round" stroke-linejoin="round"
                    d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>

            <div>Add representation</div>
        </button>
    </div>






    </div>



</div>
</div>
</div>
    <div class="w-1/2 py-10 px-8" v-if="results.length>0">

        

    
<div class="relative overflow-x-auto shadow-md sm:rounded-lg" v-if="selectedAtom == null || selectedAtom[&apos;model&apos;]!=1">
    <table class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
                <th scope="col" class="px-6 py-3">
                    
                </th>
                <th scope="col" class="px-6 py-3 text-center">
                    Location
                </th>
                <th scope="col" class="px-6 py-3 text-center">
                    Identity
                </th>
               
                <th scope="col" class="px-6 py-3 text-center">
                    Geometry
                </th>
                <th scope="col" class="px-6 py-3 text-center">
                    
                </th>
            </tr>
        </thead>
        <tbody>
            <tr 
            v-for="result in results" :key="results.index"
            class="odd:bg-white odd:dark:bg-gray-900 even:bg-gray-50 even:dark:bg-gray-800 border-b dark:border-gray-700">
                <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                    {{result.index}}
                </th>
                <td class="px-6 py-4 text-center">
                    {{result.location_confidence}}
                </td>
                <td class="px-6 py-4">
                    <span class="text-gray-800">{{labels[findMaxValueIndex(result.probabilities_identity)]}} </span><br><span class="text-sm text-gray-500 font-mono"> p={{findMaxValue(result.probabilities_identity)}}</span>
                </td>
                <td class="px-6 py-4">
                    <span class="text-gray-800">
                        {{labels_geometry[findMaxValueIndex(result.probabilities_geometry)]}} </span><br>
                    <span class="text-sm text-gray-500 font-mono"> p={{findMaxValue(result.probabilities_geometry)}}</span>
                </td>
                <td class="px-6 py-4">
                    <button 
                    @click="selectAtom(1, &apos;&apos;, result.index)"
                    class="font-medium text-blue-600 dark:text-blue-500 hover:text-blue-800"><svg class="h-6 w-6" data-slot="icon" fill="none" stroke-width="1.5" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"></path>
                      </svg></button>
                </td>
            </tr>
           
        </tbody>
    </table>
</div>


        
        <div class=" relative" v-if="selectedAtom != null && currentResult != undefined && selectedAtom[&apos;model&apos;]==1">
            <div class="absolute top-0 right-0 m-4">
                <button class="p-2 hover:bg-gray-100 rounded" @click="closeHighlight()">
                    <svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="w-6 h-6" >
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                </button>
                
            </div>

        
        <div class="flex flex-col" >
            <div class="-m-1.5 overflow-x-auto">
              <div class="p-3 min-w-full inline-block align-middle">
                <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden dark:bg-slate-900 dark:border-gray-700">
                  <!-- Header -->
                  <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                    <div class="font-bold text-lg text-orange-800">
                      Metal #{{selectedAtom.resi}}
                    </div>
                    <div class="grid grid-cols-2 py-2">

                    <div class="flex flex-col items-center justify-start my-3">
                      <p class="font-medium text-gray-900 dark:text-white mr-2">Location confidence</p>
                      <p class="bg-orange-100 text-orange-800 text-sm font-semibold inline-flex items-center p-1.5 rounded dark:bg-orange-200 dark:text-orange-800"><code>p={{currentResult.location_confidence}}</code></p>
                      <!-- <span class="w-1 h-1 mx-2 bg-gray-900 rounded-full dark:bg-gray-500"></span> -->
                      <!-- <a href="#" class="text-xs font-medium text-gray-600 hover:underline dark:text-orange-500">About this metric</a> -->
                    </div>
                    
                    <div class="flex flex-col items-center justify-start my-3">
                      <p class="font-medium text-gray-900 dark:text-white mr-2">Identity</p>
                      <p class="bg-orange-100 text-orange-800 text-sm font-semibold inline-flex items-center p-1.5 rounded dark:bg-orange-200 dark:text-orange-800">
                      
                            {{labels[findMaxValueIndex(currentResult.probabilities_identity)]}} <code class="px-2"> p={{findMaxValue(currentResult.probabilities_identity)}}</code>
                    
                    </p>
                      <!-- <p class="px-2"></p> -->
                      <!-- <span class="w-1 h-1 mx-2 bg-gray-900 rounded-full dark:bg-gray-500"></span> -->
                      <!-- <a href="#" class="text-xs font-medium text-gray-600 hover:underline dark:text-orange-500">About this metric</a> -->
                    </div>

                    <div class="mt-3 flex">
                      <div class="font-medium text-sm text-gray-900 dark:text-white mr-2">Close residues </div>
                      <div class="text-xs flex space-x-1" >
                        <span class="bg-gray-100 rounded p-1 whitespace-nowrap" v-for="r in currentResult.close_residues" :key="r.chain+&apos;&apos;+r.resi"
                        
                        >{{r.chain}}: {{r.resn}} {{r.resi}}</span>
                      </div>
                      <button class="mx-2 p-1 text-sm border border-gray-100 rounded-lg text-gray-800" @click="toggleRepresentation(0, currentResult.close_residues)"> <span v-if="toggleRepIndex==null">Show</span><span v-else>Hide</span></button>
                      
        
                    </div>
                  </div>
        
                  <div class="border-b border-gray-200 dark:border-gray-700">    
           <p class="px-4 pt-2 text-sm font-bold uppercase">Identity</p>       
        <div class="gap-4 sm:grid sm:grid-cols-2 p-4" style="gap: 0.75rem;">
              <dl v-for="(p, i) in currentResult.probabilities_identity" :key="&apos;p&apos;+i">
                  <dt class="text-sm  text-gray-500 dark:text-gray-400"><span class="font-medium">{{labels[i]}}</span></dt>
                  <dd class="flex items-center mb-3">
                      <div class="w-full bg-gray-200 rounded h-2.5 dark:bg-gray-700 mr-2">
                          <div class="bg-orange-600 h-2.5 rounded dark:bg-orange-500" :style="&apos;width:&apos;+p*100+&apos;%&apos;"></div>
                      </div>
                      <span class="text-sm font-medium text-gray-500 dark:text-gray-400">{{Math.ceil(p*100)}}%</span>
                  </dd>
              </dl>
        </div>
    </div>
       

        <div class="border-b border-gray-200 dark:border-gray-700">
            <p class="px-4 pt-2 text-sm font-bold uppercase">Geometry</p>       
            <div class="gap-4 sm:grid sm:grid-cols-2 p-4" style="gap: 0.75rem;">
                  <dl v-for="(p, i) in currentResult.probabilities_geometry" :key="&apos;p&apos;+i">
                      <dt class="text-sm  text-gray-500 dark:text-gray-400"><span class="font-medium">{{labels_geometry[i]}}</span></dt>
                      <dd class="flex items-center mb-3">
                          <div class="w-full bg-gray-200 rounded h-2.5 dark:bg-gray-700 mr-2">
                              <div class="bg-orange-600 h-2.5 rounded dark:bg-orange-500" :style="&apos;width:&apos;+p*100+&apos;%&apos;"></div>
                          </div>
                          <span class="text-sm font-medium text-gray-500 dark:text-gray-400">{{Math.ceil(p*100)}}%</span>
                      </dd>
                  </dl>
            </div>

        </div>


        </div>
       
        
        </div>
          </div>
        </div>
          
    </div>
  
        </div>       

    </div>
     <div class="w-1/2 py-10 px-8" v-else>


<div class="bg-gray-50 border border-gray-200 text-sm text-gray-600 rounded-lg p-4 dark:bg-white/10 dark:border-white/10 dark:text-neutral-400" role="alert" tabindex="-1" aria-labelledby="hs-link-on-right-label">
  <div class="flex">
    <div class="shrink-0">
      <svg class="shrink-0 size-4 mt-0.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 16v-4"></path>
        <path d="M12 8h.01"></path>
      </svg>
    </div>
    <div class="flex-1 md:flex md:justify-between ms-2">
      <p id="hs-link-on-right-label" class="text-sm">
        No metals found
      </p>
    </div>
  </div>
</div>

</div>
</div>
    <script src="https://duerrsimon.github.io/allmetal3d/_static/script_novacancy.js"></script>
</body>
</html>
"""