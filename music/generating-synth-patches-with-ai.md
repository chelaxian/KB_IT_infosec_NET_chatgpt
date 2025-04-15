# Generating Synth Patches with AI

## Table of Contents

<!-- TOC start (generated with https://bitdowntoc.derlin.ch/) -->
- [People Worth Following / Watching](#people-worth-following--watching)
- [Generating Synth Patches with AI](#generating-synth-patches-with-ai-1)
- [Audio Datasets](#audio-datasets)
- [AI Synths / Plugins / etc](#ai-synths--plugins--etc)
  - [`ableton-mcp`](#ableton-mcp)
  - [Unsorted](#unsorted)
- [Synths](#synths)
- [Synth Patches](#synth-patches)
- [Learning Manual Synth Patch Design](#learning-manual-synth-patch-design)
- [Interacting with VSTs from code](#interacting-with-vsts-from-code)
- [Reverse engineering Serum patch format](#reverse-engineering-serum-patch-format)
- [Parsing preset files from code (`.fxp`/`.fxb`/`.vstpreset`)](#parsing-preset-files-from-code-fxpfxbvstpreset)
- [Rendering a Vital Synth Patch to audio from CLI](#rendering-a-vital-synth-patch-to-audio-from-cli)
- [Unsorted](#unsorted-1)
- [Musings](#musings)
- [See Also](#see-also)
  - [My Other Related Deepdive Gist's and Projects](#my-other-related-deepdive-gists-and-projects)
<!-- TOC end -->

## People Worth Following / Watching

In no particular order:

- https://twitter.com/dadabots
  - > Research `@Harmonai_org`
  - https://dadabots.com/
    - https://dadabots.com/science/
- https://twitter.com/Harmonai_org
  - > AI for musicians, by musicians. Creators of `@StableAudio`. Part of `@StabilityAI`
  - https://www.harmonai.org/
  - https://github.com/Harmonai-org/
    - > A Stability AI lab focused on open-source generative audio models
- https://twitter.com/GoodGood014
  - > ML  / Audio Core `@BandLab`. ex `@tiktok_us` `@sutdsg`. ML & music tech
  - https://gudgud96.github.io/
  - https://github.com/gudgud96
- https://twitter.com/naughtttt
  - > techno-dharma bum building AI tools for musicians and producers. fmr MLE, DL researcher, physics + neurosci grad
  - musai demo - making ambient dnb: https://www.youtube.com/watch?v=XAEb2KnRAho
- https://twitter.com/ken_wheeler
  - > hey, ex music producer, long time programmer here. was reading a gist of yours about generating synth patches
    > i'm looking to do this as part of a talk about ai for music in april

## Generating Synth Patches with AI

- See also:
  - [AI Synths / Plugins / etc](#ai-synths--plugins--etc)
- https://micromusic.tech/
  - > The AI-Powered Vital Preset Generator
  - > MicroMusic does the hard part for you.
    > You input an audio sample, and it outputs a Vital preset file. It's that simple. Behind the scenes MicroMusic uses state-of-the-art machine learning to find the optimal parameters to create the closest matching preset it can.
  - https://micromusic.tech/app
    - Web-based version of the app
  - https://www.patreon.com/MicroMusic932
  - https://www.youtube.com/watch?v=CXFtFgRvhW8
    - > NEW AI Synth Replicator: MicroMusic
- https://ctag.media.mit.edu/
  - > Creative Text-to-Audio Generation via Synthesizer Programming (2024)
  - > Neural audio synthesis methods now allow specifying ideas in natural language. However, these methods produce results that cannot be easily tweaked, as they are based on large latent spaces and up to billions of uninterpretable parameters. We propose a text-to-audio generation method that leverages a virtual modular sound synthesizer with only 78 parameters. Synthesizers have long been used by skilled sound designers for media like music and film due to their flexibility and intuitive controls. Our method, CTAG, iteratively updates a synthesizer's parameters to produce high-quality audio renderings of text prompts that can be easily inspected and tweaked. Sounds produced this way are also more abstract, capturing essential conceptual features over fine-grained acoustic details, akin to how simple sketches can vividly convey visual concepts. Our results show how CTAG produces sounds that are distinctive, perceived as artistic, and yet similarly identifiable to recent neural audio synthesis models, positioning it as a valuable and complementary tool.
  - https://github.com/PapayaResearch/ctag
    - > Creative Text-to-Audio Generation via Synthesizer Programming (CTAG)
    - > Code for the paper Creative Text-to-Audio Generation via Synthesizer Programming. CTAG is a method for generating sounds from text prompts by using a virtual modular synthesizer. CTAG depends on SynthAX, a fast modular synthesizer in JAX.
      > 
      > You can hear many examples on the website. The code to obtain the results from the paper will be found in a different repository (coming soon).
      - https://github.com/PapayaResearch/ctag-experiments
    - https://github.com/PapayaResearch/ctag#configuration
      - > We use Hydra to configure ctag. The configuration can be found in `ctag/conf/config.yaml`, with specific sub-configs in sub-directories of `ctag/conf/`.
        - https://github.com/facebookresearch/hydra
          - > Hydra
            > Hydra is a framework for elegantly configuring complex applications
          - https://hydra.cc/
    - https://github.com/PapayaResearch/ctag#hyperparameters
      - > We use AX to sweep the hyperparameters of an algorithm with just a config field.
        - https://github.com/facebook/Ax
          - > Ax Platform
            > Adaptive Experimentation Platform
          - > Ax is an accessible, general-purpose platform for understanding, managing, deploying, and automating adaptive experiments.
            > 
            > Adaptive experimentation is the machine-learning guided process of iteratively exploring a (possibly infinite) parameter space in order to identify optimal configurations in a resource-efficient manner. Ax currently supports Bayesian optimization and bandit optimization as exploration strategies. Bayesian optimization in Ax is powered by BoTorch, a modern library for Bayesian optimization research built on PyTorch.
            - https://github.com/pytorch/botorch
              - > BoTorch
              - > BoTorch is a library for Bayesian Optimization built on PyTorch.
              - https://botorch.org/
          - https://ax.dev/
- https://github.com/DiffAPF/TB-303
  - > Differentiable All-pole Filters for Time-varying Audio Systems
  - > Time-varying subtractive synth experiments source code for "Differentiable All-pole Filters for Time-varying Audio Systems".
  - > Time-varying Subtractive Synthesizer (Roland TB-303 Bass Line) Experiments
  - https://diffapf.github.io/web/
  - https://arxiv.org/abs/2404.07970
    - > Differentiable All-pole Filters for Time-varying Audio Systems (2024)
    - > Infinite impulse response filters are an essential building block of many time-varying audio systems, such as audio effects and synthesisers. However, their recursive structure impedes end-to-end training of these systems using automatic differentiation. Although non-recursive filter approximations like frequency sampling and frame-based processing have been proposed and widely used in previous works, they cannot accurately reflect the gradient of the original system. We alleviate this difficulty by re-expressing a time-varying all-pole filter to backpropagate the gradients through itself, so the filter implementation is not bound to the technical limitations of automatic differentiation frameworks. This implementation can be employed within any audio system containing filters with poles for efficient gradient evaluation. We demonstrate its training efficiency and expressive capabilities for modelling real-world dynamic audio systems on a phaser, time-varying subtractive synthesiser, and feed-forward compressor. We make our code available and provide the trained audio effect and synth models in a VST plugin at this https URL
    - > Phaser (Electro-Harmonix Small Stone)
      > For our first experiment, we use our time domain filter to model the Electro-Harmonix SmallStone phaser pedal using the differentiable phaser architecture shown in Figure 2. The Electro-Harmonix SmallStone's circuit consists of four cascaded analog all-pass filters, a through-path for the input signal, and a feedback path which means it is topologically similar to our phaser implementation. The pedal consists of one knob which controls the LFO rate, and a switch that engages the feedback loop.
    - > Time-varying Subtractive Synthesizer (Roland TB-303 Bass Line)
      > For our second experiment, we use our time domain filter to model the Roland TB-303 Bass Line synthesizer which defined the acid house electronic music movement of the late 1980s. The TB-303 is an ideal synth for our use case because its defining feature is a resonant low-pass filter where the cutoff frequency is modulated quickly using an envelope to create its signature squelchy, “liquid” sound. We model it using the time-varying subtractive synth architecture shown in Figure 3 which consists of three main components: a monophonic oscillator, a time-varying biquad filter, and a waveshaper for adding distortion to the output. The dataset is made from Sample Science’s royalty free Abstract 303 sample pack consisting of 100 synth loops at 120 BPM recorded dry from a hardware TB-303 clone.
      - https://www.samplescience.info/2022/05/abstract-303.html
    - > Feed-forward Compressor (LA-2A Leveling Amplifier)
      > For our third experiment, we use our time domain filter to learn the parameters for the Universal Audio LA-2A analog compressor. We optimise our proposed differentiable feed-forward compressor to match the target audio, examining its capability to replicate and infer the parameters of dynamic range controllers. We train and evaluate our compressor on the SignalTrain dataset, which consists of paired data recorded in 44.1 kHz from the LA-2A compressor with different peak reduction values.
      - https://zenodo.org/records/3824876
        - > SignalTrain LA2A Dataset
        - https://arxiv.org/abs/1905.11928
          - > SignalTrain: Profiling Audio Compressors with Deep Neural Networks (2019)
            > In this work we present a data-driven approach for predicting the behavior of (i.e., profiling) a given non-linear audio signal processing effect (henceforth "audio effect"). Our objective is to learn a mapping function that maps the unprocessed audio to the processed by the audio effect to be profiled, using time-domain samples. To that aim, we employ a deep auto-encoder model that is conditioned on both time-domain samples and the control parameters of the target audio effect. As a test-case study, we focus on the offline profiling of two dynamic range compression audio effects, one software-based and the other analog. Compressors were chosen because they are a widely used and important set of effects and because their parameterized nonlinear time-dependent nature makes them a challenging problem for a system aiming to profile "general" audio effects. Results from our experimental procedure show that the primary functional and auditory characteristics of the compressors can be captured, however there is still sufficient audible noise to merit further investigation before such methods are applied to real-world audio processing workflows.
          - https://github.com/drscotthawley/signaltrain
            - > SignalTrain
              > Learning time-dependent nonlinear audio effects with neural networks
    - > We make the trained effect models accessible using the Neutone platform and SDK. This enables most users to experiment with the models via a real-time VST plugin in their preferred digital audio workstation (DAW) on arbitrary input audio.
- https://github.com/christhetree/mod_extraction
  - > Modulation Extraction for LFO-driven Audio Effects
  - > Source code for "Modulation Extraction for LFO-driven Audio Effects"
  - https://christhetr.ee/mod_extraction/
  - https://arxiv.org/abs/2305.13262
    - > Modulation Extraction for LFO-driven Audio Effects (2023)
    - > Low frequency oscillator (LFO) driven audio effects such as phaser, flanger, and chorus, modify an input signal using time-varying filters and delays, resulting in characteristic sweeping or widening effects. It has been shown that these effects can be modeled using neural networks when conditioned with the ground truth LFO signal. However, in most cases, the LFO signal is not accessible and measurement from the audio signal is nontrivial, hindering the modeling process. To address this, we propose a framework capable of extracting arbitrary LFO signals from processed audio across multiple digital audio effects, parameter settings, and instrument configurations. Since our system imposes no restrictions on the LFO signal shape, we demonstrate its ability to extract quasiperiodic, combined, and distorted modulation signals that are relevant to effect modeling. Furthermore, we show how coupling the extraction model with a simple processing network enables training of end-to-end black-box models of unseen analog or digital LFO-driven audio effects using only dry and wet audio pairs, overcoming the need to access the audio effect or internal LFO signal. We make our code available and provide the trained audio effect models in a real-time VST plugin.
- https://github.com/dafaronbi/Multi-Task-Automatic-Synthesizer-Programming
  - > Multi Task Automatic-Synthesizer-Programming
    > This is the code for the multi VST automatic synthesizer programming project. this software was used in the 2023 ICASSP paper Exploring Approaches to Multi-Task Automatic Synthesizer Programming
  - https://ieeexplore.ieee.org/document/10095540
    - > Exploring Approaches to Multi-Task Automatic Synthesizer Programming (2023)
    - > Automatic Synthesizer Programming is the task of transforming an audio signal that was generated from a virtual instrument, into the parameters of a sound synthesizer that would generate this signal. In the past, this could only be done for one virtual instrument. In this paper, we expand the current literature by exploring approaches to automatic synthesizer programming for multiple virtual instruments. Two different approaches to multi-task automatic synthesizer programming are presented. We find that the joint-decoder approach performs best. We also evaluate the performance of this model for different timbre instruments and different latent dimension sizes.
- https://github.com/gudgud96/syntheon
  - > Syntheon
  - > Syntheon provides parameter inference for music synthesizers using deep learning models. Given an audio sample, Syntheon infers the best parameter preset for a given synthesizer that can recreate the audio sample.
  - Found via: https://forum.vital.audio/t/has-anyone-tried-syntheon-for-vital-synplant-ai-for-vital/13617
  - https://www.youtube.com/watch?v=nZ560W6bA3o
    - > Parameter Inference of Music Synthesizers with Deep Learning - Hao Hao Tan - ADC22
      > 
      > Synthesizers are crucial for designing sounds in today's music. However, to create the desired sound texture by tuning the right synthesizer parameters, one requires years of training and in-depth domain experience on sound design. Music producers might also search through preset banks, but it takes extensive time and effort to find the best preset that gives the desired texture.
      > 
      > Imagine a program that you can drop your desired audio sample, and it automatically generates the synthesizer preset that could recreate the sound. This task is commonly known as "parameter inference" of music synthesizers, which could be a useful tool for sound design. In this talk, we will discuss how deep learning techniques can be used towards solving this task. We will cover recent works that use deep learning to perform parameter inference on a variety of synthesizers (FM, wavetable, etc.), as well as the challenges that were faced in solving this task.
    - https://docs.google.com/presentation/d/1PA4fom6QvCW_YG8L0MMVumrAluljcymndNlaK2HW5t0/
      - > ADC 2022 Parameter Inference
      - TODO: There seem to be lots of good papers/etc referenced in these slides.. worth copying them out here for easier reference
    - https://gudgud96.github.io/publications/
      - > Publications / Talks
- https://github.com/PapayaResearch/synthax
  - > SynthAX: A Fast Modular Synthesizer in JAX
  - > Accelerating audio synthesis far beyond realtime speeds has a significant role to play in advancing intelligent audio production techniques. SynthAX is a fast virtual modular synthesizer written in JAX. At its peak, SynthAX generates audio over 90,000 times faster than realtime, and significantly faster than the state-of-the-art in accelerated sound synthesis. It leverages massive vectorization and high-throughput accelerators.
  - > This project is based on torchsynth
  - Colab: https://colab.research.google.com/github/PapayaResearch/synthax/blob/main/examples/walkthrough.ipynb
    - > SynthAX Walk-through
      > We walk through basic functionality of synthax in this Jupyter notebook.
- https://github.com/torchsynth/torchsynth
  - > torchsynth
    > A GPU-optional modular synthesizer in pytorch, 16200x faster than realtime, for audio ML researchers.
  - > torchsynth is based upon traditional modular synthesis written in pytorch. It is GPU-optional and differentiable.
    > 
    > Most synthesizers are fast in terms of latency. torchsynth is fast in terms of throughput. It synthesizes audio 16200x faster than realtime (714MHz) on a single GPU. This is of particular interest to audio ML researchers seeking large training corpora.
    > 
    > Additionally, all synthesized audio is returned with the underlying latent parameters used for generating the corresponding audio. This is useful for multi-modal training regimes.
  - https://torchsynth.readthedocs.io/en/latest/
    - https://torchsynth.readthedocs.io/en/latest/modular-design/new-synths.html
- https://github.com/spiegelib/spiegelib
  - > SpiegeLib
    > Synthesizer Programming with Intelligent Exploration, Generation, and Evaluation Library.
  - > An object oriented Python library for research and development related to Automatic Synthesizer Programming. SpiegeLib contains a set of classes and base classes for developing and evaluating algorithms for generating parameters and patch settings for synthesizers.
  - https://spiegelib.github.io/spiegelib/
- https://github.com/SlavaCat118/Vinetics
  - > Vinetics
    > Genetics for vital
  - Found via: https://forum.vital.audio/t/vinetics-a-vital-preset-merger-by-me/9770
    - > Take an infinite number of presets and combine their features with the power of Vinetics! Combine similar presets to discover new possibilities, or pair up contrasting presets to create fresh and unique sounds!
- https://github.com/Sound2Synth/Sound2Synth
  - > Sound2Synth: Interpreting Sound via FM Synthesizer Parameters Estimation
    > This is the code repo for the paper "Sound2Synth: Interpreting Sound via FM Synthesizer Parameters Estimation" (IJCAI 2022 AI, THE ARTS AND CREATIVITY (SPECIAL TRACK)).
  - https://arxiv.org/abs/2205.03043
    - > Sound2Synth: Interpreting Sound via FM Synthesizer Parameters Estimation (2022)
    - > Synthesizer is a type of electronic musical instrument that is now widely used in modern music production and sound design. Each parameters configuration of a synthesizer produces a unique timbre and can be viewed as a unique instrument. The problem of estimating a set of parameters configuration that best restore a sound timbre is an important yet complicated problem, i.e.: the synthesizer parameters estimation problem. We proposed a multi-modal deep-learning-based pipeline Sound2Synth, together with a network structure Prime-Dilated Convolution (PDC) specially designed to solve this problem. Our method achieved not only SOTA but also the first real-world applicable results on Dexed synthesizer, a popular FM synthesizer.
  - https://github.com/Sound2Synth/Sound2Synth-Plug-Ins
    - > Sound2Synth Plug-Ins
      > This is the plug-in repo for the Sound2Synth project, which aims at helping estimate synthesizer parameters given the desired sound textures.
    - > Currently we support Sound2Synth on Dexed only, modified from the original Dexed synthesizer.
      - https://github.com/asb2m10/dexed
        - > Dexed - FM Plugin Synth
- https://github.com/christhetree/serum_rnn
  - > Code for SerumRNN
  - https://github.com/christhetree/serum_rnn/tree/master/data/presets
    - > Serum Presets (`*.fxp`)
  - https://github.com/christhetree/serum_rnn_website
    - > Audio Examples for SerumRNN
  - https://icewithfrosting.github.io/serum_rnn_examples/
    - > SerumRNN Audio Examples
    - > For each preset in each preset group (12 presets total), 20 random audio samples with 2 to 5 random effects applied are generated.
      > One example is then selected for each preset as the target audio such that the resulting examples are unique and collectively showcase a variety of different effect parameters and sounds.
  - https://www.youtube.com/watch?v=pHlEAXEux5c
    - > Christopher Mitcheltree - SerumRNN: A White-box Audio VST Effect Programming System
  - https://arxiv.org/abs/2104.03876
    - > SerumRNN: Step by Step Audio VST Effect Programming (2021)
    - > Learning to program an audio production VST synthesizer is a time consuming process, usually obtained through inefficient trial and error and only mastered after years of experience. As an educational and creative tool for sound designers, we propose SerumRNN: a system that provides step-by-step instructions for applying audio effects to change a user's input audio towards a desired sound. We apply our system to Xfer Records Serum: currently one of the most popular and complex VST synthesizers used by the audio production community. Our results indicate that SerumRNN is consistently able to provide useful feedback for a variety of different audio effects and synthesizer presets. We demonstrate the benefits of using an iterative system and show that SerumRNN learns to prioritize effects and can discover more efficient effect order sequences than a variety of baselines.
  - https://arxiv.org/abs/2102.03170
    - > White-box Audio VST Effect Programming (2021)
    - > Learning to program an audio production VST plugin is a time consuming process, usually obtained through inefficient trial and error and only mastered after extensive user experience. We propose a white-box, iterative system that provides step-by-step instructions for applying audio effects to change a user's audio signal towards a desired sound. We apply our system to Xfer Records Serum: currently one of the most popular and complex VST synthesizers used by the audio production community. Our results indicate that our system is consistently able to provide useful feedback for a variety of different audio effects and synthesizer presets.
- https://jakespracher.medium.com/generating-musical-synthesizer-patches-with-machine-learning-c52f66dfe751
  - > Generating Musical Synthesizer Patches with Machine Learning (2021)
  - https://github.com/jakespracher/ml-synth-preset-generator/
    - > Generating Musical Synthesizer Patches with Machine Learning
      > This repo accompanies this blog post. The premise is to generate high-quality presets for the Ableton Analog synthesizer in a particular style automatically using generative machine learning models.
  - > I tried generating presets using two different models: a variational autoencoder (VAE) and a generative adversarial network (GAN). The GAN had better performance, as it is a more sophisticated model.
  - > I tried various architectures, one of the best performing was the Wasserstein GAN. The one I implemented was based on this tutorial.
    - https://machinelearningmastery.com/how-to-code-a-wasserstein-generative-adversarial-network-wgan-from-scratch/
      - > How to Develop a Wasserstein Generative Adversarial Network (WGAN) From Scratch
  - > More powerful synths will make training the GAN more challenging as they have many more configuration parameters than Ableton Analog. Additionally, there is the aforementioned issue of software interoperability: we can’t easily read and write presets for the most popular synths. What would it look like to get this working with a synth like Serum?
    > 
    > VST fxp presets follow a predefined structure [based on a specification](http://jvstwrapper.sourceforge.net/vst20spec.pdf). However, Serum presets are “Opaque Chunk” format meaning the data we care about is an opaque sequence of ones and zeros.
    > 
    > Fortunately, it is still possible to make some sense of them. I was able to figure out that the chunk data is compressed by Zlib. We can decompress, make arbitrary single changes, and compare the result to the initial patch to reverse engineer the format.
    > 
    > It would also theoretically be possible to build a VST host that loads the synthesizers, manipulates parameters, and writes presets using the VST interface but writing a custom VST host seemed like a lot of work so I figured it would be easier to start with the XML.
    - http://jvstwrapper.sourceforge.net/vst20spec.pdf
  - > The networks that I’ve built fully rely on the preset configuration parameters as the training data the network learns from. An additional possibility that would be much harder to set up would be to also use the waveform generated by the sound as input to the model. I suspect this could significantly improve performance because the waveform is what a human would use to determine the aesthetic desirability of a sound. However, generating these waveforms from entire preset libraries in a suitable format would require a lot of scripting work.
- https://github.com/gwendal-lv/preset-gen-vae
  - > preset-gen-vae
  - > This repository provides models and data to learn how to program a Dexed FM synthesizer (DX7 software clone) from an input sound. Models based on Variational Autoencoders (VAE) and results are described in the DAFx 2021 paper and the companion website.
  - https://github.com/gwendal-lv/preset-gen-vae/blob/main/synth/dexed_presets.sqlite
    - > Dexed presets SQLite main database (> 30k presets)
  - https://gwendal-lv.github.io/preset-gen-vae/
    - > Improving Synthesizer Programming from Variational Autoencoders Latent Space
      > Accompanying material for the DAFx21 paper “Improving Synthesizer Programming from Variational Autoencoders Latent Space”
  - https://ieeexplore.ieee.org/document/9768218
    - > Improving Synthesizer Programming From Variational Autoencoders Latent Space (2021)
    - > Deep neural networks have been recently applied to the task of automatic synthesizer programming, i.e., finding optimal values of sound synthesis parameters in order to reproduce a given input sound. This paper focuses on generative models, which can infer parameters as well as generate new sets of parameters or perform smooth morphing effects between sounds. We introduce new models to ensure scalability and to increase performance by using heterogeneous representations of parameters as numerical and categorical random variables. Moreover, a spectral variational autoencoder architecture with multi-channel input is proposed in order to improve inference of parameters related to the pitch and intensity of input sounds. Model performance was evaluated according to several criteria such as parameters estimation error and audio reconstruction accuracy. Training and evaluation were performed using a 30k presets dataset which is published with this paper. They demonstrate significant improvements in terms of parameter inference and audio accuracy and show that presented models can be used with subsets or full sets of synthesizer parameters.
    - https://dafx2020.mdw.ac.at/proceedings/papers/DAFx20in21_paper_7.pdf
- https://www.reddit.com/r/synthesizers/comments/hn7pg9/i_trained_an_ai_to_generate_synth1_presets/
  - > I trained an AI to generate Synth1 Presets (2020)
  - > This site allows you to generate preset banks for the famous free VST plugin Synth1 using an AI I built and trained myself. I hope you find this interesting, and if you make any tracks using it I'd love to know!
    - https://www.thispatchdoesnotexist.com/
      - > Daichi Laboratory's Synth1 is a virtual synthesizer based off of the Nord Lead 2 and is the most downloaded synth plug-in of all time.
        > Click the floating synth above (or here), and an AI will generate a zipped bank of 128 presets for Synth1.
      - > This project was heavily inspired by Nintorac's This DX7 Cartridge Does Not Exist. Make sure to check that out also!
        - https://www.thisdx7cartdoesnotexist.com/
          - > The Yamaha DX7 is a classic synthesizer often cited as the sound of the 80's, this site uses a specially trained AI to create completely novel preset cartridges.
          - > If you are interested in the code it can be found here though it is mostly undocumented.
            - https://github.com/Nintorac/NeuralDX7
              - > Random machine learning experiments related to the classic Yamaha DX7
      - > I used a Generative Adversarial Network (GAN), which is essentially making two neural networks fight against each other for our own benefit.
        > The AI is made up of two parts, a generator and a discriminator. The discriminator learns to detect whether a given preset is fake or not, while the generator learns how to fool the discriminator. Over time, the discriminator gets better at detecting fakes, while the generator gets better at generating fakes. At the end, the generator ends up producing pretty convincing fakes, which are then sent to you!
        > The names are generated from a Recurrent Neural Network (RNN) based off of the synth parameters. There's a lot of duplicates however, further training and model finagling is needed.
        > If you want a more technical explanation, check out this additional blog post I wrote.
        - https://jamesskripchuk.com/TPDNE/
          - > How I Made an AI Generate Synth1 Presets (2020)
        - https://github.com/jskripchuk/Synth1GAN
          - > A GAN to generate preset banks for famous and free VST plugin Synth1
- https://arxiv.org/abs/1812.06349
  - > InverSynth: Deep Estimation of Synthesizer Parameter Configurations from Audio Signals (2018)
  - > Sound synthesis is a complex field that requires domain expertise. Manual tuning of synthesizer parameters to match a specific sound can be an exhaustive task, even for experienced sound engineers. In this paper, we introduce InverSynth - an automatic method for synthesizer parameters tuning to match a given input sound. InverSynth is based on strided convolutional neural networks and is capable of inferring the synthesizer parameters configuration from the input spectrogram and even from the raw audio. The effectiveness InverSynth is demonstrated on a subtractive synthesizer with four frequency modulated oscillators, envelope generator and a gater effect. We present extensive quantitative and qualitative results that showcase the superiority InverSynth over several baselines. Furthermore, we show that the network depth is an important factor that contributes to the prediction accuracy.
  - https://github.com/crodriguez1a/inver-synth
    - > inver-synth
      > A Python implementation of the InverSynth method
  - https://github.com/inversynth/InverSynth2
    - > InverSynth2
- https://ieeexplore.ieee.org/abstract/document/8323327
  - > Automatic Programming of VST Sound Synthesizers Using Deep Networks and Other Techniques (2018)
  - > Programming sound synthesizers is a complex and time-consuming task. Automatic synthesizer programming involves finding parameters for sound synthesizers using algorithmic methods. Sound matching is one application of automatic programming, where the aim is to find the parameters for a synthesizer that cause it to emit as close a sound as possible to a target sound. We describe and compare several sound matching techniques that can be used to automatically program the Dexed synthesizer, which is a virtual model of a Yamaha DX7. The techniques are a hill climber, a genetic algorithm, and three deep neural networks that have not been applied to the problem before. We define a sound matching task based on six sets of sounds, which we derived from increasingly complex configurations of the Dexed synthesis algorithm. A bidirectional, long short-term memory network with highway layers performed better than any other technique and was able to match sounds closely in 25% of the test cases. This network was also able to match sounds in near real time, once trained, which provides a significant speed advantage over previously reported techniques that are based on search heuristics. We also describe our open source framework, which makes it possible to repeat our study, and to adapt it to different synthesizers and algorithmic programming techniques.
  - https://research.gold.ac.uk/id/eprint/22516/1/myk_lf_vsti_programming.pdf
  - https://github.com/yeeking/deepvstprogrammers
    - > Automatic VST synthesizer programmers
    - > This repository contains a set of automatic VST synthesizer programmers, as described in
      > 
      > Automatic Programming of VST Sound Synthesizers using Deep Networks and Other Techniques IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE Matthew Yee-king, Leon Fedden and Mark d'Inverno
      >
      > This code was developed by Leon Fedden under supvision by Matthew Yee-King
- https://github.com/RichardYang40148/Neural_Wavetable_Synthesizer
  - > Neural Wavetable: a playable wavetable synthesizer using neural networks
  - > A wavetable synthesizer VST that uses WaveNet to interpolate between different wavetables. We include two formats of this synthesizer, a plug-and-play VST you can download and play RIGHT NOW in your DAW! For the more technically inclined, we also include all our source python and c++ code using tensorflow and JUCE for you to experiment and build upon.
  - > What is Wavetable synthesis?
    > If you listen and produce electronic music, you've already heard wavetable synthesis in action. A popular wavetable synthesizer used by many electronic artists is Serum. The new Ableton Live 10 also features a new Wavetable synthesizer called...you guessed it: Wavetable. The synthesizer works by using a variety of "wavetables" that define one period of the waveform. This reference wavetable is then "read" at different speeds to produce the desired pitch of sound.
  - > What is WaveNet?
    > WaveNet is the future of sound! It is a neural network architecture that has revolutionized many aspects of audio, including groundbreaking speech synthesis and new kinds of synthesis techniques.
    - https://deepmind.google/discover/blog/wavenet-a-generative-model-for-raw-audio/
      - > WaveNet: A generative model for raw audio (2016)
    - https://nsynthsuper.withgoogle.com/
      - > NSynth Super is part of an ongoing experiment by Magenta: a research project within Google that explores how machine learning tools can help artists create art and music in new ways.
      - > Magenta created NSynth (Neural Synthesizer). It’s a machine learning algorithm that uses a deep neural network to learn the characteristics of sounds, and then create a completely new sound based on these characteristics.
      - > Since the release of NSynth, Magenta have continued to experiment with different musical interfaces and tools to make the output of the NSynth algorithm more easily accessible and playable.
        > 
        > As part of this exploration, they've created NSynth Super in collaboration with Google Creative Lab. It’s an open source experimental instrument which gives musicians the ability to make music using completely new sounds generated by the NSynth algorithm from 4 different source sounds.
  - > What is a Neural WaveTable?
    > We use WaveNet to encode some basic wavetables like a Sin, Triangle and Sawtooth - all with length 512 - into WaveNet's latent space. Each of these sounds are now represented by a real-valued "embedding vector" of length 16. This vector encapsulates sonic and timbral characteristics of the original wavetable. We then interpolate between these wavetables, not by adding or subtracting them directly, but by mixing their latent vectors. For example, 30% sin and 70% saw means "find the embedding that is 30% away from the vector of sin and 70% away from the vector of saw". We then use the newly interpolated vector to decode back into the original wavetable of length 512. To make the decoded wavetables play nice, we normalize all wavetables and also include an option to "smooth" the wave.
  - https://arxiv.org/abs/1811.05550
    - > Neural Wavetable: a playable wavetable synthesizer using neural networks (2018)
    - > We present Neural Wavetable, a proof-of-concept wavetable synthesizer that uses neural networks to generate playable wavetables. The system can produce new, distinct waveforms through the interpolation of traditional wavetables in an autoencoder's latent space. It is available as a VST/AU plugin for use in a Digital Audio Workstation.

## Audio Datasets

- https://magenta.tensorflow.org/datasets/nsynth
  - > The NSynth Dataset
    > A large-scale and high-quality dataset of annotated musical notes.
  - > NSynth is an audio dataset containing 305,979 musical notes, each with a unique pitch, timbre, and envelope. For 1,006 instruments from commercial sample libraries, we generated four second, monophonic 16kHz audio snippets, referred to as notes, by ranging over every pitch of a standard MIDI pian o (21-108) as well as five different velocities (25, 50, 75, 100, 127). The note was held for the first three seconds and allowed to decay for the final second.
    > 
    > Some instruments are not capable of producing all 88 pitches in this range, resulting in an average of 65.4 pitches per instrument. Furthermore, the commercial sample packs occasionally contain duplicate sounds across multiple velocities, leaving an average of 4.75 unique velocities per pitch.
    > 
    > We also annotated each of the notes with three additional pieces of information based on a combination of human evaluation and heuristic algorithms:
    > 
    > - Source: The method of sound production for the note’s instrument. This can be one of acoustic or electronic for instruments that were recorded from acoustic or electronic instruments, respectively, or synthetic for synthesized instruments. See their frequencies below.
    > - Family: The high-level family of which the note’s instrument is a member. Each instrument is a member of exactly one family. See the complete list and their frequencies below.
    > - Qualities: Sonic qualities of the note. See the quality descriptions and their co-occurrences below. Each note is annotated with zero or more qualities.
- https://guitarset.weebly.com/
  - > GuitarSet
  - > GuitarSet, a dataset that provides high quality guitar recordings alongside rich annotations and metadata.
    >
    > In particular, by recording guitars using a hexaphonic pickup, we are able to not only provide recordings of the individual strings but also to largely automate the expensive annotation process, therefore providing rich annotation.
    > 
    > The dataset contains recordings of a variety of musical excerpts played on an acoustic guitar, along with time-aligned annotations including pitch contours, string and fret positions, chords, beats, downbeats, and playing style.
- https://egfxset.github.io/
  - > EGFxSet (2022)
  - > 8970 five-second length audio recordings of real electric guitar sounds
  - > All notes of a standard tuning electric guitar processed through 12 different effects
  - > EGFxSet contains recordings of all clean tones in a Stratocaster guitar, with augmentations by processing the audios through twelve electric guitar effects. Similar datasets apply effects using software, EGFxSet in contrast uses real guitar effects hardware, making it relevant to develop MIR tools with applications on real music. Annotations include all guitar and effect parameters controlled during our dataset recording. EGFxSet contains 8970 unique, annotated guitar tones, and is published with full open-access rights.
  - https://zenodo.org/records/7044411#.YzRx2XbMKUl
    - > EGFxSet: Electric guitar tones processed through real effects of distortion, modulation, delay and reverb
    - > EGFxSet (Electric Guitar Effects dataset) features recordings for all clean tones in a 22-fret Stratocaster, recorded with 5 different pickup configurations, also processed through 12 popular guitar effects. Our dataset was recorded in real hardware, making it relevant for music information retrieval tasks on real music. We also include annotations for parameter settings of the effects we used.
- https://zenodo.org/records/7544110
  - > IDMT-SMT-Guitar Dataset (2023)
  - > The IDMT-SMT-GUITAR database is a large database for automatic guitar transcription. Seven different guitars in standard tuning were used with varying pick-up settings and different string measures to ensure a sufficient diversification in the field of electric and acoustic guitars. The recording setup consisted of appropriate audio interfaces, which were directly connected to the guitar output or in one case to a condenser microphone. The recordings are provided in one channel RIFF WAVE format with 44100 Hz sample rate.
    > 
    > The dataset consists of four subsets. The first contains all introduced playing techniques (plucking styles: finger-style, muted, picked; expression styles: normal, bending, slide, vibrato, harmonics, dead-notes) and is provided with a bit depth of 24 Bit. It has been recorded using three different guitars and consists of about 4700 note events with monophonic and polyphonic structure. As a particularity the recorded files contain realistic guitar licks ranging from monophonic to polyphonic instrument tracks.
    > 
    > The second subset of data consists of 400 monophonic and polyphonic note events each played with two different guitars. No expression styles were applied here and each note event was recorded and stored in a separate file with a bit depth of 16 Bit. The parameter annotations for the first and second subset are stored in XML format.
    > 
    > The third subset is made up of five short monophonic and polyphonic guitar recordings. All five pieces have been recorded with the same instrument and no special expression styles were applied. The files are stored with a bit depth of 16 Bit and each file is accompanied by a parameter annotation in XML format.
    > 
    > Additionally, a fourth subset is included, which was created for evaluation purposes in the context of chord recognition and rhythm style estimation tasks. This set contains recordings of 64 short musical pieces grouped by genre. Each piece has been recorded at two different tempi with three different guitars and is provided with a bit depth of 16 Bit. Annotations regarding onset positions, chords, rhythmic pattern length, and texture (monophony/polyphony) are included in various file formats.
- https://github.com/torchsynth/synth1K1
  - > Github.io page for hosting the the synth1K1 dataset
  - https://torchsynth.github.io/synth1K1/
- https://www.kaggle.com/datasets/odysseask/synth1-dataset
  - > Synth1 Dataset
  - > A dataset of parameters and sounds generated using the Synth1 VST
- https://torchsynth.readthedocs.io/en/latest/reproducibility/synth1B1.html
  - > SYNTH1B1
  - > synth1B1 is a corpus consisting of one million hours of audio: one billion 4-second synthesized sounds. The corpus is multi-modal: Each sound includes its corresponding synthesis parameters.
    > 
    > synth1B1 is generated on the fly by torchsynth 1.x, using the Voice synth with its default settings.
  - > Researchers can denote subsamples of this corpus as synth1M1, synth10M1, etc., which would refer to the first 1 million and 10 million samples of Synth1B1 respectively.
- https://zenodo.org/records/4680486
  - > ARTURIA synthesizer sounds dataset
  - > This dataset contains all data that have been used in: Roche F., Hueber T., Garnier M., Limier S. and Girin L., 2021. "Make That Sound More Metallic: Towards a Perceptually Relevant Control of the Timbre of Synthesizer Sounds Using Variational Autoencoder". Transactions of the International Society for Music Information Retrieval.
    > 
    > It is constituted of a .zip file containing 1,233 audio samples of synthesizer sounds generated using factory presets of ARTURIA software applications resulting in single pitched sounds (E3, ~165Hz) with a similar duration (between 2 and 2.5 seconds) and normalized in loudness.
- https://synthdatasets.weebly.com/
  - > Synth Datasets
  - > Welcome to the companion website for the synthesized datasets published as part of the following paper:
    >
    > An analysis/synthesis framework for automatic f0 annotation of multitrack datasets
    > J. Salamon, R. M. Bittner, J. Bonada, J. J. Bosch, E. Gómez, and J. P. Bello. 
    > In 18th Int. Soc. for Music Info. Retrieval Conf., Suzhou, China, Oct. 2017.
    - https://www.justinsalamon.com/uploads/4/3/9/4/4394963/salamon_f0synthannotation_ismir_2017.pdf
      - > Generating continuous f0 annotations for tasks such as melody extraction and multiple f0 estimation typically involves running a monophonic pitch tracker on each track of a multitrack recording and manually correcting any estimation errors. This process is labor intensive and time consuming, and consequently existing annotated datasets are very limited in size. In this paper we propose a framework for automatically generating continuous f0 annotations without requiring manual refinement: the estimate of a pitch tracker is used to drive an analysis/synthesis pipeline which produces a synthesized version of the track. Any estimation errors are now reflected in the synthesized audio, meaning the tracker’s output represents an accurate annotation. Analysis is performed using a wide-band harmonic sinusoidal modeling algorithm which estimates the frequency, amplitude and phase of every harmonic, meaning the synthesized track closely resembles the original in terms of timbre and dynamics. Finally the synthesized track is automatically mixed back into the multitrack. The framework can be used to annotate multitrack datasets for training learning-based algorithms. Furthermore, we show that algorithms evaluated on the automatically generated/annotated mixes produce results that are statistically indistinguishable from those they produce on the original, manually annotated, mixes. We release a software library implementing the proposed framework, along with new datasets for melody, bass and multiple f0 estimation.
  - > The datasets are intended for research on monophonic, melody, bass, and multiple f0 estimation (pitch tracking), and include:
    >
    > - MDB-melody-synth: 65 songs from the MedleyDB dataset in which the melody track has been resynthesized to obtain a perfect melody f0 annotation using the analysis/synthesis method described in the paper.
    > - MDB-bass-synth: 71 songs from the MedleyDB dataset in which the bass track has been resynthesized to obtain a perfect bass f0 annotation using the analysis/synthesis method described in the paper.
    > - MDB-mf0-synth: 85 songs from the MedleyDB dataset in which polyphonic pitched instruments (such as piano and guitar) have been removed and all monophonic pitched instruments (such as bass and voice) have been resynthesized to obtain perfect f0 annotations using the analysis/synthesis method described in the paper.
    > - MDB-stem-synth: 230 solo stems (tracks) from the MedleyDB dataset spanning a variety of musical instruments and voices, which have been resynthesized to obtain a perfect f0 annotation using the analysis/synthesis method described in the paper.
    > - Bach10-mf0-synth: 10 classical music pieces (four-part J.S. Bach chorales) from the Bach10 dataset where each instrument (bassoon, clarinet, saxophone and violin) has been resynthesized to obtain perfect f0 annotations using the analysis/synthesis method described in the paper.
    - https://medleydb.weebly.com/
      - > MedleyDB: A Dataset of Multitrack Audio for Music Research

## AI Synths / Plugins / etc

### `ableton-mcp`

- https://github.com/ahujasid/ableton-mcp
  - > AbletonMCP - Ableton Live Model Context Protocol Integration
  - > AbletonMCP connects Ableton Live to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Ableton Live. This integration enables prompt-assisted music production, track creation, and Live session manipulation.
  - > Features
    > - **Two-way communication**: Connect Claude AI to Ableton Live through a socket-based server
    > - **Track manipulation**: Create, modify, and manipulate MIDI and audio tracks
    > - **Instrument and effect selection**: Claude can access and load the right instruments, effects and sounds from Ableton's library
    > - **Clip creation**: Create and edit MIDI clips with notes
    > - **Session control**: Start and stop playback, fire clips, and control transport
  - https://www.anthropic.com/news/model-context-protocol
    - > Introducing the Model Context Protocol
  - https://www.youtube.com/watch?v=QXSImhfS15k
    - > YouTube: AI controls my ABLETON LIVE Project 🤯 AbletonMCP installation Tutorial and Testing

### Unsorted

- https://neutone.ai/
  - > Neutone
  - > Next Generation AI tools for Musicians and Artists
- https://soniccharge.com/synplant
  - > Synplant takes a genetic twist on sound design by moving beyond traditional knob-twisting and dial-adjusting, emphasizing exploration and discovery. Here, your ears guide you through a forest of organic textures and evolving timbres.
  - > Genopatch crafts synth patches from audio recordings, using AI to find optimal synth settings based on your source sample. As the strands in the user interface sprout and grow, they generate patches that increasingly match the chosen audio.
- https://guk.ai/sistema-ai-synthesizer
  - > Sistema is the first AI-powered software instrument that helps you easily create pro-quality sounds for your music.
  - > Sistema uses AI models to provide a endless new sounds and textures, helping you to overcome creative blocks. Unique preset names add a fun twist to each session.
  - > Sistema's advanced technology produces high-quality sound without the clutter of traditional synthesizers. Control various aspects of your sounds with the built-in macro collection featuring multiple effects.
  - > Create or tweak sounds in any genre from Hip-Hop, EDM, Rock & Pop to House, Indie & Metal.
  - > US$149 or US$30/mo for 6 months

## Synths

A short list of some software synths that might be useful to explore generating patches for:

- Vital: https://vital.audio/
  - > Spectral warping wavetable synth
- Serum: https://xferrecords.com/products/serum/
  - > Advanced Wavetable Synthesizer
  - https://xferrecords.com/preset_packs
- Native Instruments Massive: https://www.native-instruments.com/en/products/komplete/synths/massive/
  - > Virtual-analog architecture for colossal sound
    > Equally flexible in the studio or on stage
    > Comprehensive library with 1,300 huge presets
- Sylenth1: https://www.lennardigital.com/sylenth1/
  - > Sylenth1 is a virtual analog VSTi synthesizer that takes the definitions of quality and performance to a higher level. Until now only very few software synthesizers have been able to stand up to the sound quality standards of hardware synths. Sylenth1 is one that does.
    > Sylenth1 is not just another synth. It was built from a producer's point of view. It was built to produce superior quality sound and music. It was built to perform. A lot of research has been invested in order to achieve unheard warmth and clarity. The graphical interface ensures the highest level of usability so you can fully unleash your creativity.
- Synth1: https://daichilab.sakura.ne.jp/softsynth/index.html
  - > This is a software synthesizer intended for use with DTM software. Compatible with VSTi plug-in/AU plug-in format. This software is freeware.
  - > Functionally, it is modeled after that red synth Clavia NORD LEAD2
- etc

## Synth Patches

- https://github.com/instatetragrammaton/Patches
  - > Patches and theory for your software synths
  - > This repository contains patches for various software synthesizers. Often, these are remakes - clean-room reverse engineered - of the sounds you can hear in popular music. Others have a more academical approach - to teach or explain certain concepts.
    > I am not a fan of "studio secrets". I have been fortunate enough to learn from many people at no cost; it is only fitting that I return the favor for others, keeping the threshold as low as possible for everyone.
- https://github.com/Miserlou/SynthRecipies
  - > Random Serum Patches
- https://vst-preset-generator.org/
  - > The VST Preset Generator is a software to create random preset for VST plugins.
  - > The VST Preset Generator writes preset files (fxp for program patch or fxb for bank patch) with randomized values.
    > This is a tool for lazy or curious sound designers, who want to experiment random theory with their VST plugins.
  - Source: https://svn.tuxfamily.org/viewvc.cgi/vpg_vst-preset-gen/

## Learning Manual Synth Patch Design

- https://www.syntorial.com/
  - > Syntorial is video game-like training software, that will teach you how to program synth patches by ear. With almost 200 lessons, combining video demonstrations with interactive challenges, you’ll get hands on experience programming patches on a built-in soft synth, and learn everything you need to know to start making your own sounds with ease.
- https://unison.audio/reverse-engineer-presets-in-serum/
  - > A Complete Guide To Reverse-Engineering Any Preset In Serum (2018)
  - Note: This is more about manually reverse engineering and re-creating the sound, not reverse engineering the Serum patch file format itself

## Interacting with VSTs from code

- https://github.com/topics/vst3-host
- https://github.com/fedden/RenderMan
  - > RenderMan
  - > Command line C++ and Python VSTi Host library with MFCC, FFT, RMS and audio extraction and `.wav` writing
  - > Renderman is a command line VSTi host written in C++ with Python bindings using JUCE and Maximilian libraries for the backend. It is designed with ease of use in mind to extract audio and features from VSTi plugins. It has a fast growing list of features, including setting, getting parameters from synthesiers, setting whole patches, getting random patches, obtaining MFCCS, FFT, audio data and much more.
    - https://github.com/micknoise/Maximilian
      - > Maximilian
      - > C++ Audio and Music DSP Library
      - > Maximilian is a cross-platform and multi-target audio synthesis and signal processing library. It was written in C++ and provides bindings to Javascript. It's compatible with native implementations for MacOS, Windows, Linux and iOS systems, as well as client-side browser-based applications. Maximilian is self-contained, and compiles without dependencies.
      - > The main features are:
        > 
        > - sample playback, recording and looping
        > - support for WAV and OGG files
        > - a selection of oscillators and filters
        > - enveloping
        > - multichannel mixing for 1, 2, 4 and 8 channel setups
        > - controller mapping functions
        > - effects including delay, distortion, chorus, flanging
        > - granular synthesis, including time and pitch stretching
        > - atom synthesis
        > - real-time music information retrieval functions: spectrum analysis, spectral features, octave analysis, Bark scale analysis, and MFCCs
        > - example projects for Windows and MacOS, susing command line and OpenFrameworks environments
        > - example projects for Firefox and Chromium-based browsers using the Web Audio API ScriptProcessorNode (deprecated!)
        > - example projects for Chromium-based browsers using the Web Audio API AudioWorklet (e.g. Chrome, Brave, Edge, Opera, Vivaldi)
        > - will run on embedded systems (e.g. ESP32, Pi Pico)
      - https://github.com/micknoise/Maximilian#web-audio
        - > Web Audio
          > A transpiled javascript version of the library is included in this repository, for both Script Processor Nodes and AudioWorklets. Try this out at (https://mimicproject.com/guides/maximJS).
        - https://github.com/Louismac/maximilian-js-local
          - > Hosting `maximilian.js`
            > If you want to run `maximilian.js` (the Web Audio version of maximilian )on something other than the mimicproject.com website, you've come to the right place.
      - https://github.com/fedden/juceSynths
        - > Collection of JUCE synthesisers utilising the Maximilian library
  - https://github.com/fedden/RenderMan#getting-parameter-descriptions
    - > Getting Parameter Descriptions
      > We can obtain the available parameters that are used and that can be modified by doing the following.
  - https://github.com/fedden/RenderMan#getting-a-randomised-patch-for-a-synthesiser
    - > Getting a Randomised Patch For a Synthesiser
      > We can easily get a randomised for a given synth by using the `PatchGenerator` class.
- https://github.com/spotify/pedalboard
  - > 🎛 🔊 A Python library for working with audio.
  - > pedalboard is a Python library for working with audio: reading, writing, rendering, adding effects, and more. It supports most popular audio file formats and a number of common audio effects out of the box, and also allows the use of VST3® and Audio Unit formats for loading third-party software instruments and effects.
  - https://github.com/spotify/pedalboard/issues/6 (Changing VST parameter throughout time?)
  - https://github.com/spotify/pedalboard/issues/96 (Pedalboard objects are not pickleable or serializable)
  - https://github.com/spotify/pedalboard/issues/160 (`[question]` `[request]` Is it possible to use `.aupreset` just like `.vstpreset`?)
    - https://github.com/spotify/pedalboard/pull/171 (Add `.aupreset` support)
      - https://forum.juce.com/t/add-getpreset-setpreset-to-audiounitclient/61430/3
        - > Add `.getPreset` / `.setPreset` to `AudioUnitClient`
  - https://github.com/spotify/pedalboard/issues/187 (Save and Load Presets Automatically for VST3 Plugins?)
    - https://github.com/spotify/pedalboard/issues/187#issuecomment-2119660508
      - > I was just reading a bit more about how this works in VST3, and it seems there are technically 2 separate types of state; the state that affects the audio, and the rest of the plugin GUI/etc state.
        > 
        > I documented some of this + reference links on another issue in this comment:
        > 
        > - https://github.com/spotify/pedalboard/pull/289#issuecomment-2119647346
        > 
        > So while I'm not 100% certain, I suspect that may be why you're seeing the difference between the audio effect and GUI.
        > 
        > ---
        > 
        > **Edit:** With regards to this bit:
        > 
        > > Or the `my_plugin.state` bytes object will cure this all?
        > 
        > The following snippet from my other post seems like it can answer it:
        > 
        > > Looking at JUCE's code we can see the implementations for:
        > > 
        > > - `AudioPluginAudioProcessor`'s `getStateInformation` / `setStateInformation`: https://github.com/juce-framework/JUCE/blob/4f43011b96eb0636104cb3e433894cda98243626/examples/CMake/AudioPlugin/PluginProcessor.h#L42-L43
        > >   - ..snip..
        > >   - `VST3PluginInstance` / `AudioPluginInstance` (`getStateInformation` / `setStateInformation`): https://github.com/juce-framework/JUCE/blob/4f43011b96eb0636104cb3e433894cda98243626/modules/juce_audio_processors/format_types/juce_VST3PluginFormat.cpp#L3055-L3109
        > >     - `getStateInformation` seems to `appendStateFrom` with both `IComponent` and `IEditController`
        > >     - `setStateInformation` also seems to have handling for both `IComponent` and `IEditController`
        > >     - so I think this JUCE state method may handle both of them in a single call, which is convenient
        > > - ..snip..
        > > 
        > > This tutorial may also be interesting for futher/deeper reading:
        > > 
        > > - https://docs.juce.com/master/tutorial_audio_processor_value_tree_state.html
        > > 
        > > _Originally posted by @0xdevalias in https://github.com/spotify/pedalboard/issues/289#issuecomment-2119647346_
        > 
        > Specifically, it seems like the `getStateInformation` / `setStateInformation` functions implemented in #297 as the `plugin.raw_state` look like they will save/restore both forms of VST3 state (`IComponent`, `IEditController`) in the one XML'ish file (assuming the VST plugin implements/has state for both)
        > 
        > _Originally posted by @0xdevalias in https://github.com/spotify/pedalboard/issues/187#issuecomment-2119660508_
  - https://github.com/spotify/pedalboard/issues/245 (Loading non `.vstpreset` files with `load_preset` function)
  - https://github.com/spotify/pedalboard/issues/257 (VST plugin Program presets not accessible)
  - https://github.com/spotify/pedalboard/issues/266 (Parameter Values)
  - https://github.com/spotify/pedalboard/issues/243 (`AudioProcessorParameter` `raw_value` Setter Problem)
  - https://github.com/spotify/pedalboard/issues/211 (ASIO Drivers support?)
  - https://github.com/spotify/pedalboard/issues/263 (ML Examples with `tf.data`)
    - https://github.com/spotify/pedalboard/blob/f2c2ccd64e78abaf9b87bc2c59097965c8b92fe5/tests/test_tensorflow.py#L34-L53
  - https://github.com/spotify/pedalboard/issues/240 (Plans to support LADSPA and LV2?)
  - https://github.com/spotify/pedalboard/issues/269 (Add Support for VST2 Plugins)
  - https://github.com/spotify/pedalboard/issues/270 (Add Support for CLAP Plugins)
  - https://github.com/spotify/pedalboard/issues/277 (Cannot load `.fxp` file for Serum)
    - `DawDreamer` example in this comment: https://github.com/spotify/pedalboard/issues/277#issuecomment-2081116603
    - https://github.com/spotify/pedalboard/issues/277#issuecomment-2119721235
      - >
        > As an example of what the XML part of the `.raw_state` output from #297 looks like, when loading a fresh instance of Serum, I used the following helpers/code:
        > 
        > - https://github.com/0xdevalias/poc-audio-pedalboard/commit/da6a2ae32423fc6d7371d46ebed7273bbc95b45e
        > 
        > ```python
        > def is_vst3_xml(raw_state):
        >     """
        >     Check if the raw state looks like VST3 XML.
        > 
        >     This function checks if the 9th to 13th bytes are '<?xml' and the last byte is a null byte (0x00).
        > 
        >     Args:
        >       raw_state (bytes): The raw state to check.
        > 
        >     Returns:
        >       bool: True if the raw state looks like VST3 XML, False otherwise.
        >     """
        >     return (
        >             len(raw_state) > 13 and
        >             raw_state[8:13] == b'<?xml' and
        >             raw_state[-1] == 0x00
        >     )
        > 
        > 
        > def extract_vst3_xml(raw_state):
        >     """
        >     Extract the XML content from the VST3 raw state if it is valid.
        > 
        >     Args:
        >       raw_state (bytes): The raw state to extract XML from.
        > 
        >     Returns:
        >       str or None: The extracted XML content if valid, otherwise None.
        >     """
        >     if is_vst3_xml(raw_state):
        >         try:
        >             # Extract the bytes between the 8-byte header and the null byte
        >             xml_part = raw_state[8:-1].decode('utf-8')
        >             return xml_part
        >         except UnicodeDecodeError:
        >             pass
        >     return None
        > ```
        > 
        > Along with this code to write out the XML part to a file:
        > 
        > - https://github.com/0xdevalias/poc-audio-pedalboard/commit/1e1a4ce95447cbd012df1b5662771be28705892e#diff-88be30bc731c22307bd8ace482b8c8ed449d56fa3ef3eab1551a6e91ffbbd5ccR252-R269
        > 
        > ```python
        > # Check and extract XML from initial state
        > if is_vst3_xml(initial_synth_raw_state):
        >     initial_synth_state_xml = extract_vst3_xml(initial_synth_raw_state)
        >     with open(args.out_state_file_initial_xml, 'w') as f:
        >         f.write(initial_synth_state_xml)
        >         print(f"Initial raw state XML written to {args.out_state_file_initial_xml}")
        > else:
        >     print("Initial state does not look like VST3 XML.")
        > 
        > # Check and extract XML from new state
        > if is_vst3_xml(new_synth_raw_state):
        >     new_synth_state_xml = extract_vst3_xml(new_synth_raw_state)
        >     with open(args.out_state_file_new_xml, 'w') as f:
        >         f.write(new_synth_state_xml)
        >         print(f"New raw state XML written to {args.out_state_file_new_xml}")
        > else:
        >     print("New state does not look like VST3 XML.")
        > ```
        > 
        > Which, after formatting it, gave me output like this for the initial state after loading Serum:
        > 
        > ```xml
        > <?xml version="1.0" encoding="UTF-8"?>
        > <VST3PluginState>
        >     <IComponent>6365.3EP6c1.bUTcEGeShDBQEBAMHnBgXEzTEDRKNP4cOg3HRnhH5TKRasDnkuZM.AET5T5iIi.p0VnLpfLsUZFasfefCSsXssBSzQpFTnnCXYnPlLVvfLhkoEKNNo2O18kMQRxBCiDd6ucl6d28dO26t6+8b9Qd2bxCOOOwytkzu1c1y5MpLLGkLoWStV5H6xHh1kYDsKqHZ24EQ65RDsK6HZWWinc4DQ65VDsK2HZ24GQ6tfHZ2EFQ65dDsqGA146dQEJ.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.J.JvYCEnjRJQ77JUWr+8CEt1b6Dzm+wlpj91b5LljJ2bl5ZYlP8latdtap9DtyM8mT9uW02VaeRy0K01uXAWynzmHaut5BrUep0F4jM9SValw2ph9TaalZu8r1jJSYg+0lTmXwEKlRacrYbautaVURIaxVrSfWR6wl1OwhWucNdh0zGwTL16WblZu2s5h+4g6Oo+ytoe6w9iMb6N60Wqf4MzXr8om2jA5k9dXM12AN6ClmB0iwT77z5ZqdGUpcL9iy+dLXbd9WK+lsZgY7IUWY44GzWPcJiZ+CLycRYCqOWcoQy8R3MaesTKr2CguF91XZ2LWeQWaulgumaqiCeOGXyIqsf9n9TSA7e+2hXqVOCA5cPso+Vcbp2ml1C0Wp18myVbcBYmYLNaCEi5OF67Ex11aNr1ZhOMbOyX7GWxPi2Lss8bDDC6GiqssP8XME6bY3XAyUPsYBE6enolir1Yud59KUWRdRXCt4xYqcL9iq4i0WGeVYRUyGmp+Vbfgq5e8aw8j1nvmGdLl1srVCuMf+5aP3wnO19rz5wF97fia03BZt8dVaw6g.tp244FZp4y7rkotjktX5qK5R15RW0kbzktoKrE6U.i6.awXEXBUMiJpbVSa9CYz2Pgy7du6gN3EVwBhwxQr6Quo1XyJDYlwn7xbIixq5spqyHwJJa.Ixq5QmXE0VQhbxbIIFaQqLwxKacI11TegD4T8VSL1Z1YhkWa8I1QCert+LTWU9cSM1h5oZlCqOpkW1.TO8sc0psM0gpNTUiPkS0iVcMqpb0MWyDU+vMcmpeZsUndlcMKUcMLO0Gdr6WkclKQUPtOfZf4+fpg22GQMlhVoZRE+n54ZMp6aj+R87sN0pG2SomyeuZyS9Y0y6Kn1yr+C549kTexh9K54eqp99vulp3U82TibsaWMtZ1oZxa3cUydSumZQu79TOTs0qdh278UqeWef5Os2indiF9X0+3v+GUiG6+oNwm9Y5qeFR2yNKofb6hzut2UYf42MYvEb9xv66EJp90CYLE0S4VFXuj6n3KVtqA2aY5CqORkC+RkELxKWVrp+xRKa.xOaLWg7Xi6Jke0sLH42daWs7b2wWVdwIesxqbWCQd8oNT4smdIxtm8WU1ekWubvpFg7QK3qIGeQIjlVrHcs5QK8XY2fz6G9Fk9+yuIYPqpbYHO9WWt90Ndoze8DjwVyDka82c6xj1v2Plxy+MkYto6Tl6e7aI22K+cjjux2UVdsUHq30mlr5276KO4aOC4o20rjMt6efr48d2xV1+bjs0v7jcbv4K64v2qbfOZgxgN18KG83+H4S9zersv6+X+6+CzTS627ySRsSGB8uMbT+eN6C7EbcnaA6gmsuOBt9A2Wmsziy92GYj5CyZ9relh+Vg5ZSwqvqsvxqbV2itxb1meaY4rwrFTp0kpvB+7VzdsbJZd6MUmQ5a7ULsplSgCsMmKW+CqC5ujNn+uRa1utif2CmEqM2CoJs9dMz8UaZSqGSGcd3qW6cbGMOmJ8atNs2Vp9eqQLCyZ3ZOeCqu3DlR6MPissb83aeqoWT.T.T.eEvm633MApRye+FlWSQytdFQ6xOh10qHZ2EEQ6t3HZWAQztdGQ6tjHZWehnc8Mh1coQztKKh1c4Qzt9EQ65efcAtbsacxCszbL+ni8tT8uw7RJIqcrzkYOO4G329TltYK6i52tWi9suk5LaWPdKy29f1cWs7LU1ejzC2h4uW2Zf8As6l+Blqtc8uwfqyMb12ZE35dPmN6cLmd1GstYr4I66ya+8XU9dpaQ6a9+So0iiyQAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPAPA5Lq.CXiUMyUdj2QVVAu2ac7a+fR8K5hzek40nLj88kxdIOZCxPy4YtrI+81kLm7qdKuw5dMogmZsuZga7eI+jY+mumUcIup7gSby86ANb8RYS482QQ68Hx+9uO9ol2jdIY0UZFvNkFGnYFZTlWhb2cMy8ckeyM9hG6ydmMKiZ+S3Qd7JazjG972sN+86ie.wAvAfC.G.N.b.3.vAfC.G.NPbfCDZ4ANf44UuE78jE0nG3OP7.b.3.vAfC.G.N.b.3.vAfCjNxAbuUI9l3ahuSGiuwuF+Z7q4eeCN.b.3.vAfC.GHdyAre2uqk.y+GvZ9u3u5cM3+6A14c3um7gf7gHNjOD3mieN94j+evAfC.G.N.b.3.vAfCD5CCSdR6DCV+LzAiBfe.9A3GPb.b.3.vAfC.G.N.bfzWNfy6N884C9E7K3WDeCG.N.b.3.vAfC.G.N.bf3JGf7jlumrah7fg7fg7fg7gCN.b.3.vAfC.G.N.b.3.g4.tkHvtm7jNttdI7baT.VuP7CvOf3.3.vAfC.G.N.b.3.wGNfyaO977BeC9F7Mh2gC.G.N.b.3.vAfC.G.NPbgCPdRSdRSdRu+v4CA4GC4GC9CjmbvAfC.G.N.b.3.vAfC3VR.6dxS53x5ivyoQAX8.wO.+.hCfC.G.N.b.3.vAfCDe4.Nu+36yO7O3ev+H9GN.b.3.vAfC.G.N.b.3.oqb.xSZxSZxSZxSZMei7Ai7Ai7Ai3.3.vAfC.G.N.b.3.MyAbKAfcO4Ic555gvykQAX89vO.+.hCfC.G.N.b.3.vAfC.GHfC3hFPOBzCpgOBeDd.b.3.vAfC.G.N.b.3.vARW3.jmzjenjmzjmzZdF4EE4EE4EEwAvAfC.G.N.b.3.vAZlC39H+18jmzoKq+AOGFEf0yC+.7CHN.N.b.3.vAfC.G.N.bf1hC3hNPeZK8g1geB+D9.b.3.vAfC.G.N.b.3.vANWkCPdRS9gRdRSdRq4WjWTjWTjWTDG.G.N.b.3.vAfC.GnYNf6i3a2SdRet55cv8sQAX85vO.+.hCfC.G.N.b.3.vAfC.GHpb.WzB5UT0KrC9J7U3EvAfC.G.N.b.3.vAfC.G3bEN.4IM4GJ4IM4IslWQdQQdQQdQQb.b.3.vAfC.G.N.bfl4.tORucO4I84JquA2mFEf0iC+.7CHN.N.b.3.vAfC.G.N.bfSWNfK5A86zU+Xbveg+B+.N.b.3.vAfC.G.N.b.3.cV4.jmzjenjmzjmzZ9D4EE4EE4EEwAvAfC.G.N.b.3.vAZlC39H718rdFcVWOCtuLJ.9m3Gfe.wAvAfC.G.N.b.3.vAfCblhC3hlPOOSomLOvmgOCOAN.b.3.vAfC.G.N.b.3.ct3.ddA4Ks695jtm7lf7lf7ln47lf3AhGHdf3A3.vAfC.G.N.b.3.oubfPenXV+hNWqeAuO38gQAvO.+.7CHN.N.b.3.vAfC.G.NvYdNfyq5L+7R7JwqDuRbEb.3.vAfC.G.N.b.3.vAfCzYfCPdRqeKPdtPdtPdtPb.b.3.vAfC.G.N.b.3.vAfCX3.g1XcabhA5.5fQAvO.+.7CHN.N.b.3.vAfC.G.NP5KGv4cm997A+B9E7KhugC.G.N.b.3.vAfC.G.NP7lCPdRqe+S9PP9PPdQQb.b.3.vAfC.G.N.b.3.vAfCPdRaWfDVmn385Dw6ed+aT.7CvO.+.hCfC.G.N.b.3.wKNf6oE+d76iW9879l22FE.+.7CvOf3.3.vAfC.G.NP7fCzw4I8+GfqgV0d3EP6Yu+9eHW+GG+IFFFlyy4ggggg47r8hc974yGYyrSrggggmIIIIIokjVRRRRRRRaOSRRRRRRRKIIIIII0W88lt99ew2O6551d7491t1O755806e4YDu2uxiyuc7QzHYMTrdh9FQWo6zaZLVlKKmjqfqgUyZ313t39n3Q3I3YX87x7571DmPDchNSWnqr8zM1M5N8fdRun2zGNF5KMFHCkQxXYhLUlIyk4yBYorbVAqjUQxkxkwkyUvUxUwUy0v0x0w0yp4F3F4lXMbybKbqbab6bGbmbWb2bObubeb+7.rVJdPdHdXdDdTdLdbdBdRdJdZdFdVdNddVOu.uHuDuLuBuJuFuNuAuIuEuMuC+adWh9EwFvFxFQmXiYSXSoyrYr4rEzE1R1J1Z5JaCaKaGaO6.6H6Dciclcgckcicm8f8jtydwdy9POXeY+X+omb.bfbPzKNXNDNT5MGFGNGA8gijihiligikiiim9xIP+n+z3D4jX.LPFDClgvPYXLbFAijQwnYLLVFGimIvDYRLYlBSkowzYFLSlEyl4vb4j4TXdLeNUV.mFKjEwhYIrTNcNCVFKmyjyhylUv4v4x4wJ474B3BYUbQbwbIj8KRh2mk3RsDueKwkYI9.VhK2R7AsDWgk3CYItRKwG1RbUVhOhk3psDeTKw0XI9XVhq0R7wsDWmk3SXItdKwmzRrZKwmxRbCVhOsk3FsDeFKwMYI9rVh0XI9bVha1R74sD2hk3KXItUKwWzRbaVhujk31sDeYKwcXI9JVh6zR7UsD2kk3qYItaKwW2RbOVhugk3dsDeSKw8YI9VVh62R7ssDOfk36XIVqkXcVhxR7csDOnk36YIdHKw22R7vVhefk3QrD+PKwiZI9QVhGyR7isDOtk3mXIdBKwO0R7jVhelk3orD+bKwSaI9EVhmwR7KsDOqk3WYIdNKwu1R77VheikX8Vheqk3ErD+NKwKZI98VhWxR7GrDurk3OZIdEKwexR7pVh+rk30rD+EKwqaI9qVh2vR72rDuok3uaIdKKw+vR71Vh+ok3crD+KKw+1R7+XIdWKw+whuDLZjTDafljhXC0jTDajljhnSZRJhMVSRQrIZRJhMUSRQzYMIEwloIoH1bMIEwVnIoH5hljhXK0jTDakljhXq0jTDcUSRQrMZRJhsUSRQrcZRJhsWSRQrCZRJhcTSRQrSZRJhtoIoH1YMIEwtnIoH1UMIEwtoIoH1cMIEwdnIoH1SMIEQ20jTD6kljhXu0jTD6iljhnGZRJh8USRQreZRJh8WSRQzSMIEwAnIoHNPMIEwAoIoH5kljh3f0jTDGhljh3P0jTD8VSRQbXZRJhCWSRQbDZRJh9nIoHNRMIEwQoIoHNZMIEwwnIoHNVMIEwwoIoHNdMIEQe0jTDmfljhneZRJh9qIoPDMRJhSTSRQbRZRJhAnIoHFnljhXPZRJhAqIoHFhljhXnZRJhgoIoHFtljhXDZRJhQpIoHFkljhXzZRJhwnIoHFqljhXbZRJhwqIoHlfljhXhZRJhIoIoHlrljhXJZRJhopIoHllljhX5ZRJhYnIoHloljhXVZRJhYqIoHliljhXtZRJhSVSRQbJZRJh4oIoHluljh3T0jTDKPSRQbZZRJhEpIoHVjljhXwZRJhknIoHVpljh3z0jTDmgljhXYZRJhkqIoHNSMIEwYoIoHNaMIEwJzjTDmiljh3b0jTDmmljhXkZRJhyWSRQbAZRJhKTSRQrJMIEwEoIoHtXMIEwknIo9uVmedc9yVm+t04eilFA0EooQPsJMMBpKTSif5BzzHnNeMMBpUpoQPcdZZDTmqlFA04noQPsBMMBpyVSif5rzzHnNSMMBpkqoQPsLMMBpyPSif5z0zHnVplFA0RzzHnVrlFA0hzzHnVnlFA0oooQPs.MMBpSUSifZ9ZZDTySSif5TzzHnNYMMBp4poQPMGMMBpYqoQPMKMMBpYpoQPMCMMBpoqoQPMMMMBpopoQPMEMMBpIqoQPMIMMBpIpoQPMAMMBpwqoQPMNMMBpwpoQPMFMMBpQqoQPMJMMBpQpoQPMBMMBpgqoQPMLMMBpgpoQPMDMMBpAqoQPMHMMBpApoQPM.MMBpSRSif5D0zHnZZZDT8WSifpeZZDTmflFAUe0zHnNdMMBpiSSif5X0zHnNFMMBpiVSif5nzzHnNRMMBp9noQPcDZZDTGtlFA0gooQP0aMMBpCUSif5PzzHnNXMMBpdooQPcPZZDTGnlFA0AnoQP0SMMBp8WSifZ+zzHn1WMMBpdnoQPsOZZDT6slFA0dooQP0cMMBp8TSifZOzzHn1cMMBpcSSifZW0zHn1EMMBpcVSifpaZZDT6jlFA0NpoQPsCZZDTaulFA01ooQPssZZDTailFAUW0zHn1ZMMBpsRSifZK0zHn5hlFA0VnoQPs4ZZDTallFAUm0zHn1TMMBpMQSifZi0zHn5jlFA0FooQPsgZZDTaflFAUnoQ7d+7+YsQP9tVx+GK4+1R9urjuik7eZIeaK4+vR9VVx+tk7Msj+MK4aXI+qVxW2R9Wrjulk7OaIeUK4exR9JVx+nk7ksj+AK4KYI+8VxWzR96rjufk72ZIWuk72XIedK4u1R9bVxekk7Ysj+RK4yXI+EVxm1R9ysjOkk7mYIeRK4O0R9DVxehk7wsj+XK4iYI+QVxG0R9CsjOhk7GXIeXK422R9PVxumk7AsjeWKYYIWmkbsVxuik7ArjeaK48aI+VVx6yR9Msj2qk7aXIuGK4W2Rd2Vxulk7trjeUK4cZI+JVx6vR9ksj2tk7KYIuMK4WzRdqVxufk7VrjedK4MaI+bVx0XI+rVxaxR9Yrj2nk7SaIuAK4mxRtZK4mzRd8VxOgk75rjebK40ZI+XVxqwR9QsjWsk7iXIuJK4G1RdkVxOjk7JrjePK4kaI+.VxKyR99sjWpk78YIS664R3h4hXUbgbAb9rRNONWNGVAmMmEmIKmkwYvoyRYIrXVDKjSiEvox7YdbJbxLWlCylYwLYFLclFSkovjYRLQl.imwwXYLLZFEijQvvYXLTFBClAw.Y.bRbhzn+zONA5KGOGGGKGCGMGEGI8gifCmCidygxgvASu3f3.4.nmr+reruzC1G1a1K5N6I6A6N6F6J6B6LcichcjcfsmsisksgtxVyVwVRWXKXyYynyrorIrwzI1H1P1.Bd2uiumm2g2l2h2j2fWmWiWkWgWlWhWjWf0yyyywyxyvSySwSxSviyiwixivCyCwCRwZ4A39493d4d3t4t3N4N31413V4V3lYMbSbibCrZtdtNtVtFtZtJtRtBtbtLtTRVEqjUvxYorPlOykYxTYhLVFICkARi9xwPen2zK5I8ftytQ2X6oqzE5Lchf29A7NyKy54Y3I3Qn393t31XMrZtFtBRVNykwRidS2oqDr9us+eXMjzHdue99s+e+pi6+2w8+2v90w8+Gf2fAxfXvLDFJCigyHXjLJFMigwx3X7LAlHShIyTXpLMlNyfYxrX1LGlKmLmByi4yoxB3zXgrHVLKgkxoyYvxX4blbVb1rBNGNWNOVImOW.WHqhKhKlKgrecb++03c3y4cfNt+u2gGz6v2yRG2+26vK5c32aoi6+2+Nt++10+Nt++9z+Nt++Qz+Nt++.88AjTDCRSRQLXMIEwPzjTDCUSRQLLMIEwv0jTDiPSRQLRMIEwnzjTDiVSRQLFMIEwX0jTDiSSRQLdMIEwDzjTDSTSRQLIMIEwj0jTDSQSRQLUMIEwzzjTDSWSRQLCMIEwL0jTDyRSRQLaMIEwbzjTDyUSRQbxZRJhSQSRQLOMIEw70jTDmpljhXAZRJhSSSRQrPMIEwhzjTDKVSRQrDMIEwR0jTDmtljh3LzjTDKSSRQrbMIEwYpIoHNKMIEwYqIoHVgljh3bzjTDmqljh37zjTDqTSRQb9ZRJhKPSRQbgZRJhUoIoHtHMIEwEqIoHtDMI0+05539+Kaccb++4rNe2v57cD97.MBpYooQPMSMMBpYnoQPMcMMBpoooQPMUMMBponoQPMYMMBpIooQPMQMMBpInoQPMdMMBpwooQPMVMMBpwnoQPMZMMBpQooQPMRMMBpQnoQPMbMMBpgooQPMTMMBpgnoQPMXMMBpAooQPMPMMBpAnoQPcRZZDTmnlFAUSSifNt+u2iC06Acb+eedXO7dPG2+2mG1JuGao2C539+qsi6++rqsi6++s74.539+dGVs2gOokNt+u2gkxRXwrHVHmFKfSk4y73T3jYtLGlMyhYxLX5LMlJSgIyjXhLAFOiiwxXXzLJFIifgyvXnLDFLChAx.3j3DoQ+oebBzWNdNNNVNFNZNJNR5CGAGNGF8lCkCgCldwAwAxAPOY+Y+XeoGrOr2rWzc1S1C1c1M1U1E1Y5F6D6H6.aOaGaKaCckslshsjtvVvlylQmYSYSXioSrQrgrADzw8+++y2+++EpTze+c7B...</IComponent>
        > </VST3PluginState>
        > ```
        > 
        > A note from my earlier deepdive into this:
        > 
        > > Specifically, it seems like the `getStateInformation` / `setStateInformation` functions implemented in #297 as the `plugin.raw_state` look like they will save/restore both forms of VST3 state (`IComponent`, `IEditController`) in the one XML'ish file (assuming the VST plugin implements/has state for both)
        > 
        > Which you can see the deeper dive in the following + linked comments:
        > 
        > > > Those saved values are applied to the VST plugin in terms of its effect on the audio. But the plugin interface doesn't show the custom values. Therefore, the updates by `setattr` are not reflected in the UI. Is there a more early phase to init a VST plugin? Or the `my_plugin.state` bytes object will cure this all?
        > > 
        > > @famzah I was just reading a bit more about how this works in VST3, and it seems there are technically 2 separate types of state; the state that affects the audio, and the rest of the plugin GUI/etc state.
        > > 
        > > I documented some of this + reference links on another issue in this comment:
        > > 
        > > - https://github.com/spotify/pedalboard/pull/289#issuecomment-2119647346
        > > 
        > > So while I'm not 100% certain, I suspect that may be why you're seeing the difference between the audio effect and GUI.
        > > 
        > > ---
        > > 
        > > **Edit:** With regards to this bit:
        > > 
        > > > Or the `my_plugin.state` bytes object will cure this all?
        > > 
        > > The following snippet from my other post seems like it can answer it:
        > > 
        > > > Looking at JUCE's code we can see the implementations for:
        > > > 
        > > > - `AudioPluginAudioProcessor`'s `getStateInformation` / `setStateInformation`: https://github.com/juce-framework/JUCE/blob/4f43011b96eb0636104cb3e433894cda98243626/examples/CMake/AudioPlugin/PluginProcessor.h#L42-L43
        > > >   - ..snip..
        > > >   - `VST3PluginInstance` / `AudioPluginInstance` (`getStateInformation` / `setStateInformation`): https://github.com/juce-framework/JUCE/blob/4f43011b96eb0636104cb3e433894cda98243626/modules/juce_audio_processors/format_types/juce_VST3PluginFormat.cpp#L3055-L3109
        > > >     - `getStateInformation` seems to `appendStateFrom` with both `IComponent` and `IEditController`
        > > >     - `setStateInformation` also seems to have handling for both `IComponent` and `IEditController`
        > > >     - so I think this JUCE state method may handle both of them in a single call, which is convenient
        > > > - ..snip..
        > > > 
        > > > This tutorial may also be interesting for futher/deeper reading:
        > > > 
        > > > - https://docs.juce.com/master/tutorial_audio_processor_value_tree_state.html
        > > > 
        > > > _Originally posted by @0xdevalias in https://github.com/spotify/pedalboard/issues/289#issuecomment-2119647346_
        > > 
        > > Specifically, it seems like the `getStateInformation` / `setStateInformation` functions implemented in #297 as the `plugin.raw_state` look like they will save/restore both forms of VST3 state (`IComponent`, `IEditController`) in the one XML'ish file (assuming the VST plugin implements/has state for both)
        > > 
        > > _Originally posted by @0xdevalias in https://github.com/spotify/pedalboard/issues/187#issuecomment-2119660508_
        > 
        > I haven't yet looked any deeper into the specific encoded output format in the XML -> `VST3PluginState` -> `IComponent` yet; nor attempted to compare/contrast it with the specific `.fxp` patch format.
        > 
        > For my more general notes on reversing the serum format, you can see this gist:
        > 
        > - https://gist.github.com/0xdevalias/5a06349b376d01b2a76ad27a86b08c1b#reverse-engineering-serum-patch-format
        > 
        > _Originally posted by @0xdevalias in https://github.com/spotify/pedalboard/issues/277#issuecomment-2119721235_
  - https://github.com/spotify/pedalboard/pull/289 (Addition: Implementing Save and Load Functionality for VST3 Plugin States)
    - https://github.com/spotify/pedalboard/pull/289#issuecomment-2119647346
      - > I was reading a bit more about saving/loading state for VST3, and it sounds like there are 2 different kinds of state:
        > - https://www.kvraudio.com/forum/viewtopic.php?t=597225
        >   - > Vst3 has 2 sets of states, a processor state, which is the state of the audio processor (all parameter values etc) , and a controller state, which is the state of the gui and everything that is unique to that and not part of the audio processing.
        >     > 
        >     > Iirc, a host calls `Processor::SetState()` with the processor state and then `EditController::SetComponentState()` with the same state, and finally `EditController::SetState()` with the controller state. Maybe not exactly in that order, but you get the idea.
        > - https://steinbergmedia.github.io/vst3_dev_portal/pages/Technical+Documentation/API+Documentation/Index.html
        >   - > A VST 3 audio effect or instrument basically consists of two parts: a processing part and an edit controller part. The corresponding interfaces are:
        >     > 
        >     > - Processor: [Steinberg::Vst::IAudioProcessor](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IAudioProcessor.html) + [Steinberg::Vst::IComponent](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IComponent.html)
        >     > - Controller: [Steinberg::Vst::IEditController](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IEditController.html)
        >   - https://steinbergmedia.github.io/vst3_dev_portal/pages/Technical+Documentation/API+Documentation/Index.html#persistence
        >     - > ## Persistence
        >       > The host stores and restores the complete state of the processor and of the controller in project files and in preset files:
        >       > 
        >       > - [Steinberg::Vst::IComponent::getState](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IComponent.html#a10db03106be8ba89d23859fa6be5d9f6) + [Steinberg::Vst::IComponent::setState](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IComponent.html#a77ac39bcc5c4b15818b1a87de2573805) store and restore the DSP model.
        >       > - [Steinberg::Vst::IEditController::getState](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IEditController.html#a10db03106be8ba89d23859fa6be5d9f6) + [Steinberg::Vst::IEditController::setState](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IEditController.html#a77ac39bcc5c4b15818b1a87de2573805) store and restore any GUI settings that are not related to the processor (like scroll positions etc).
        >       > - Restore: When the states are restored, the host passes the processor state to both the processor and the controller ([Steinberg::Vst::IEditController::setComponentState](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IEditController.html#a4c2e1cafd88143fda2767a9c7ba5d48f)). A host must always pass that state to the processor first. The controller then has to synchronize its parameters to this state (but must not perform any [IComponentHandler](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IComponentHandler.html) callbacks). After restoring a state, the host rescans the parameters (asking the controller) in order to update its internal representation.
        >       
        > Am I right in assuming that previously we were able to access the 'processor state' (param values), and as of #297 we can now access the 'controller state'?
        > 
        > ---
        > 
        > **Edit:** Looking at the code in the PR ([Ref](https://github.com/spotify/pedalboard/pull/297/files#diff-92c3a773d7741c96eca66bf6693f69f042d059419d439571dc4e269f7c504d64R1279-R1285)) it calls `pluginInstance->getStateInformation` and `pluginInstance->setStateInformation`; which appear to be JUCE methods:
        > 
        > - https://docs.juce.com/master/classAudioProcessor.html#a5d79591b367a7c0516e4ef4d1d6c32b2
        >   - > `getStateInformation()`
        >     > `virtual void AudioProcessor::getStateInformation (juce::MemoryBlock & destData)`
        >     > The host will call this method when it wants to save the processor's internal state.
        >     > 
        >     > This must copy any info about the processor's state into the block of memory provided, so that the host can store this and later restore it using `setStateInformation()`.
        >     > 
        >     > Note that there's also a `getCurrentProgramStateInformation()` method, which only stores the current program, not the state of the entire processor.
        >     > 
        >     > See also the helper function `copyXmlToBinary()` for storing settings as XML.
        > - https://docs.juce.com/master/classAudioProcessor.html#a6154837fea67c594a9b35c487894df27
        >   - > `setStateInformation()`
        >     > `virtual void AudioProcessor::setStateInformation (const void * data, int sizeInBytes)`
        >     > This must restore the processor's state from a block of data previously created using `getStateInformation()`.
        >     > 
        >     > Note that there's also a `setCurrentProgramStateInformation()` method, which tries to restore just the current program, not the state of the entire processor.
        >     > 
        >     > See also the helper function `getXmlFromBinary()` for loading settings as XML.
        > 
        > Those docs also mention these following different methods:
        > 
        > - https://docs.juce.com/master/classAudioProcessor.html#aa8f9774ef205e4b19174f2de7664928f
        >   - > `getCurrentProgramStateInformation()`
        >     > `virtual void AudioProcessor::getCurrentProgramStateInformation(juce::MemoryBlock &destData)`
        >     > The host will call this method if it wants to save the state of just the processor's current program.
        >     > 
        >     > Unlike `getStateInformation`, this should only return the current program's state.
        >     > 
        >     > Not all hosts support this, and if you don't implement it, the base class method just calls `getStateInformation()` instead. If you do implement it, be sure to also implement `setCurrentProgramStateInformation`.
        > - https://docs.juce.com/master/classAudioProcessor.html#ade2c2df3606218b0f9fa1a3a376440a5
        >   - > `setCurrentProgramStateInformation()`
        >     > `virtual void AudioProcessor::setCurrentProgramStateInformation(const void * data, int  sizeInBytes)`
        >     > The host will call this method if it wants to restore the state of just the processor's current program.
        >     > 
        >     > Not all hosts support this, and if you don't implement it, the base class method just calls `setStateInformation()` instead. If you do implement it, be sure to also implement `getCurrentProgramStateInformation`.
        > - https://docs.juce.com/master/classAudioProcessor.html#a6d0c1c945bebbc967d187c0f08b42c4b
        >   - > `copyXmlToBinary()`
        >     > `static void AudioProcessor::copyXmlToBinary(const XmlElement & xml, juce::MemoryBlock & destData)`
        >     > Helper function that just converts an xml element into a binary blob.
        >     > 
        >     > Use this in your processor's `getStateInformation()` method if you want to store its state as xml.
        >     > 
        >     > Then use `getXmlFromBinary()` to reverse this operation and retrieve the XML from a binary blob.
        > - https://docs.juce.com/master/classAudioProcessor.html#a80c616e54758a0a411d27d6d76df956c
        >   - > `getXmlFromBinary()`
        >     > `static std::unique_ptr< XmlElement > AudioProcessor::getXmlFromBinary(const void * data, int sizeInBytes)`
        >     > Retrieves an XML element that was stored as binary with the `copyXmlToBinary()` method.
        >     > 
        >     > This might return nullptr if the data's unsuitable or corrupted.
        > 
        > Looking at JUCE's code we can see the implementations for:
        > 
        > - `AudioPluginAudioProcessor`'s `getStateInformation` / `setStateInformation`: https://github.com/juce-framework/JUCE/blob/4f43011b96eb0636104cb3e433894cda98243626/examples/CMake/AudioPlugin/PluginProcessor.h#L42-L43
        >   - https://github.com/juce-framework/JUCE/blob/4f43011b96eb0636104cb3e433894cda98243626/examples/CMake/AudioPlugin/PluginProcessor.cpp#L168-L181
        >     - > You should use this method to store your parameters in the memory block.
        >       > You could do that either as raw data, or use the XML or ValueTree classes
        >       > as intermediaries to make it easy to save and load complex data.
        >   - `VST3PluginInstance` / `AudioPluginInstance` (`getStateInformation` / `setStateInformation`): https://github.com/juce-framework/JUCE/blob/4f43011b96eb0636104cb3e433894cda98243626/modules/juce_audio_processors/format_types/juce_VST3PluginFormat.cpp#L3055-L3109
        >     - `getStateInformation` seems to `appendStateFrom` with both `IComponent` and `IEditController`
        >     - `setStateInformation` also seems to have handling for both `IComponent` and `IEditController`
        >     - so I think this JUCE state method may handle both of them in a single call, which is convenient
        > - `setComponentState`, which calls `Vst::EditController::setComponentState`: https://github.com/juce-framework/JUCE/blob/master/modules/juce_audio_plugin_client/juce_audio_plugin_client_VST3.cpp#L1034-L1060
        > - `EditController` (which has `setComponentState`, `getState`, `setState`, etc): https://github.com/juce-framework/JUCE/blob/master/modules/juce_audio_processors/format_types/VST3_SDK/public.sdk/source/vst/vsteditcontroller.h#L68
        > - `PresetFile::restoreComponentState`, which calls `editController->setComponentState`: https://github.com/juce-framework/JUCE/blob/master/modules/juce_audio_processors/format_types/VST3_SDK/public.sdk/source/vst/vstpresetfile.cpp#L500-L509
        > - etc
        > 
        > This tutorial may also be interesting for futher/deeper reading:
        > 
        > - https://docs.juce.com/master/tutorial_audio_processor_value_tree_state.html
        > 
        > _Originally posted by @0xdevalias in https://github.com/spotify/pedalboard/issues/289#issuecomment-2119647346_
  - https://github.com/spotify/pedalboard/pull/297 (Add binary state field to VST3 and AU plugins)
    - https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.VST3Plugin.raw_state
      - > A bytes object representing the plugin’s internal state.
        > For the VST3 format, this is usually an XML-encoded string prefixed with an 8-byte header and suffixed with a single null byte.
    - https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.AudioUnitPlugin.raw_state
      - > A bytes object representing the plugin’s internal state.
        > For the Audio Unit format, this is usually a binary property list that can be decoded or encoded with the built-in `plistlib` package.
  - https://github.com/spotify/pedalboard/issues/329 (Can we connect a VST instrument to an AudioStream?)
- https://github.com/DBraun/DawDreamer
  - > Digital Audio Workstation with Python; VST instruments/effects, parameter automation, FAUST, JAX, Warp Markers, and JUCE processors
  - https://dirt.design/DawDreamer/
    - > DawDreamer Documentation
    - https://dirt.design/DawDreamer/dawdreamer.html
  - https://github.com/DBraun/DawDreamer/tree/main/examples/
  - https://github.com/DBraun/DawDreamer/wiki/DawDreamer-Wiki
    - > DawDreamer Wiki
  - https://github.com/DBraun/DawDreamer/wiki/Release-Notes
    - > Release Notes
  - https://github.com/DBraun/DawDreamer/wiki/Plugin-Compatibility
    - > Plugin Compatibility
  - https://github.com/DBraun/DawDreamer/wiki/Plugin-Processor
    - > Plugin Processor
  - https://github.com/DBraun/DawDreamer/wiki/Playback-Warp-Processor
    - > Playback Warp Processor
    - > Pitch-stretching and Time-stretching with Warp Markers
    - > (For a companion project related to warp markers, see AbletonParsing)
      - https://github.com/DBraun/AbletonParsing
        - > Parse an Ableton ASD clip file (warp markers and more) in Python
    - > Time-stretching and pitch-stretching are currently available thanks to Rubber Band Library.
      - https://github.com/breakfastquay/rubberband/
        - > Official mirror of Rubber Band Library, an audio time-stretching and pitch-shifting library.
        - https://breakfastquay.com/rubberband/
          - > Rubber Band Library is a high quality software library for audio time-stretching and pitch-shifting. It permits you to change the tempo and pitch of an audio stream or recording dynamically and independently of one another.
  - https://github.com/DBraun/DawDreamer/wiki/Faust-Processor
    - > Faust Processor
  - https://github.com/DBraun/DawDreamer/wiki/Other-Processors
    - > Other Processors
  - https://github.com/DBraun/DawDreamer/wiki/Render-Engine-and-BPM
    - > Render Engine and BPM
- https://github.com/PortAudio/portaudio
  - > PortAudio is a cross-platform, open-source C language library for real-time audio input and output.
  - https://www.portaudio.com/
  - https://people.csail.mit.edu/hubert/pyaudio/
    - > PyAudio
      > PyAudio provides Python bindings for PortAudio v19, the cross-platform audio I/O library. With PyAudio, you can easily use Python to play and record audio on a variety of platforms, such as GNU/Linux, Microsoft Windows, and Apple macOS.
      > 
      > PyAudio is distributed under the MIT License.
  - https://github.com/spatialaudio/python-sounddevice
    - > Play and Record Sound with Python
      >
      > This Python module provides bindings for the PortAudio library and a few convenience functions to play and record NumPy arrays containing audio signals.
      > 
      > The sounddevice module is available for Linux, macOS and Windows.
    - https://python-sounddevice.readthedocs.io/
- https://github.com/ramirezd42/vst-js
  - > native node addon that allows for instantiation of natively installed VST3 audio plugins
- https://github.com/ZECTBynmo/node-vst-host
  - > A (thin) wrapper for MrsWatson that allow you to use node.js to process audio files with VST plugins
  - https://github.com/teragonaudio/MrsWatson
    - > A command-line VST plugin host
    - https://teragonaudio.com/MrsWatson.html
      - > NOTE: This software is unsupported and is no longer being updated or maintained. It likely will not work on newer versions of macOS.
      - > MrsWatson is a command-line audio plugin host. It takes an audio and/or MIDI file as input, and processes it through one or more audio plugins. Currently MrsWatson only supports VST 2.x plugins, but more formats are planned in the future. MrsWatson was designed for primarily three purposes:

## Reverse engineering Serum patch format

- From a podcast with Steve Duda (2025), at 53:08'ish he talks about wanting to open-source the preset format at some point:
  - https://youtu.be/QmbM-eP-zQw?list=PLDxTQYPyq4JQzYc29ltUgBh8LkMVnNFbl&t=3188
    - > I do think about opening up the serum preset format which is something that I'd like to do at some point in the future um so that if someone wanted to make a utility to try to convert some synth presets into serum or vice versa that they would have more um more access to being able to attempt that or like AI generate presets and stuff like that which I personally am a little opposed to but I I don't really want to stop people from trying so right now serum presets when I say serum preset I mean serum 2 preset they're a Json format but it's like Json compressed so it's not human readable um and we do that not only to save disk space but also it actually loads a lot faster so it's more performant um but in theory we could have an option that you could save as with it uncompressed and then at that point you're left with like you have with Ableton Live you have this sort of human readable file describing everything that's been moved off of its default value um and that can be kind of interesting um it would take a lot of work for someone but in theory someone could make you know Python scripts or whatever it is that could generate presets from script or whatever it is they'd want to imagine uh but we have to sort of provide them with that and documentation first so um it's not a priority probably serum 2.1 or 2.5 though I'd like I would like to open that up to people
- https://www.reddit.com/r/edmproduction/comments/69hxa7/reverse_engineering_serums_fxp_files/
  - > Reverse engineering Serum's .fxp files? (2017)
  - > I'm trying to build a program to generate new presets for Serum. Serum stores them as a .fxp file, which seems to be a header followed by opaque data. Is there documentation on how to extract parameter values from these files somewhere, or am I out of luck?
  - > Update: I reached out to Steve through Xfer's forum and he was prompt and helpful. Unfortunately, the .fxp file format is completely dependent on the source code, and he can't release a spec for it without making the code open source. Which probably isn't happening any time soon.
- Random notes from decompilation:
  - Entrypoint/loading/saving/etc:
    - `_VSTPluginMain` -> `createEffectInstance` -> - ?`SerumPlugEdit::SerumPlugEdit`? -> (`SerumDSP::SerumDSP`, `SerumGUI::SerumGUI`)
    - `SerumDSP::SerumDSP` -> `SerumDSP::CheckForDefaultFXPAndLoad` -> `SerumDSP::LoadPreset`
    - (`SerumGUI::openControls`, `SerumGUI::valueChanged`) -> (`SerumGUI::notify`, `SerumGUI::DialogNotifier`) -> `SerumGUI::SavingPresetStuff` -> `SerumDSP::SavePreset`
  - ```
    002f7730  void** juce::SystemStats::getJUCEVersion(void** arg1)
    ..snip..
    002f7759      __builtin_strcpy(dest: &rax_1[4], src: "JUCE v6.0.4")
    ..snip..
    ```
    - https://github.com/juce-framework/JUCE/releases/tag/6.0.4
      - https://github.com/juce-framework/JUCE/releases/download/6.0.4/juce-6.0.4-osx.zip
    - > ChatGPT: To create a package that contains all the JUCE headers and sources for your project, similar to the `JuceLibraryCode` folder found in JUCE's examples and extras, you would typically use the Projucer, JUCE's project management tool.
    - It seems that Projucer also lets us pick the C++ Language Standard that will be used for the project, and defaults to C++14 (options are C++11, C++14, C++17, use latest)
    - Choosing C++11 raised a warning that "Module(s) have a higher C++ standard requirements than project."
    - Once that is done, we can add a path like this to the 'Compiler Flags' section of Binary Ninja: `-I/Users/devalias/Desktop/path/to/juce-6.0.4-osx/modules`
    - And attempt to import the `JuceHeader.h` file
    - But in doing so we get an error lile this, which apparently could be resolved by pointing Binary Ninja at the C++ standard libraries (even though I believe it already should be.. so maybe we don't have the 'right' c++ standard libraries installed by default?):
      - ```
        error: /Users/devalias/Desktop/path/to/juce-6.0.4-osx/modules/juce_analytics/juce_analytics.h:54:10 'queue' file not found
        1 error generated.
        ```
      - https://stackoverflow.com/questions/7630277/including-queue-in-c-program-in-ubuntu-os
      - https://docs.brew.sh/C++-Standard-Libraries
      - https://apple.stackexchange.com/questions/414622/installing-a-c-c-library-with-homebrew-on-m1-macs
        - This talks about adding the homebrew include path (eg. `/usr/local/include`) for the imports; but we have already done that based on the 'Finding System Headers' section of the Binary Ninja docs
          - https://docs.binary.ninja/guide/types/typeimportexport.html#finding-system-headers
      - https://developer.apple.com/xcode/cpp/
        - > C++ language support
          > Apple supports C++ with the Apple Clang compiler (included in Xcode) and the libc++ C++ standard library runtime (included in SDKs and operating systems). The compiler and runtime are regularly updated to offer new functionality, including many leading-edge features specified by the ISO C++ standard.
    - Even if we remove the `juce_analytics` module within Projucer and attempt to re-import into Binary Ninja, we end up with an error like this:
      - ```
        error: /Users/devalias/Desktop/path/to/juce-6.0.4-osx/modules/juce_core/system/juce_TargetPlatform.h:56:3 "No global header file was included!"
        error: /Users/devalias/Desktop/path/to/juce-6.0.4-osx/modules/juce_core/system/juce_StandardHeader.h:46:10 'algorithm' file not found
        2 errors generated.
        ```
        - To fix the `juce_TargetPlatform.h:56:3 "No global header file was included!"` part of the error, within Projucer, select the 'Project Settings', scroll down to 'Use Global AppConfig Header', and change it from 'Disabled' to 'Enabled'. When this is disabled, these settings are injected via the build system, which means we would need to specify those settings to Binary Ninja in a more manual way.. enabling it seems to simplify that step.
        - To fix the C++ standard library not being found error(s), they seem to go away when we specify a full path to the c++ includes, rather than just pointing to the higher level path
          - ```
            -isystem/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include/c++/v1/
            -isystem/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include
            -isystem/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/15.0.0/include
            -isystem/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include
            -I/Users/devalias/Desktop/path/to/juce-6.0.4-osx/modules
            ```
        - Though after doing that, I end up with a different error (unsure if related to the above being the wrong approach to take):
          - ```
            error: /Users/devalias/Desktop/path/to/juce-6.0.4-osx/modules/juce_core/streams/juce_InputStream.h:261:5 CType::TemplateSpecialization not implemented
            1 error generated.
            ```
          - As best I can currently figure out.. this might be a limitation of Binary Ninja's header importer.. though I'm not 100% sure about that
  - Looking at serum presets, we can see various chunks of data at the start of the file like: `CcnK`, `BFPCh`, `XfsX`, etc (along with some non-printable hex characters)
    - Searching for `CcnK` showed a few variations (`CcnK`, `CcnKH`, `CcnKL`), with the most relevant looking code snippets being the following:
      - `char const chunkheader[0x5] = "CcnK", 0`
      - `void* data_7d46c8 = chunkheader {"CcnK"}`
      - `int64_t SerumDSP::SavePreset(int64_t* arg1)`
    - Searching for `BFPCh` didn't turn up anything, but `FPCh` did, with the most relevant looking code snippets being the following:
      - `char const data_67cfa8[0x5] = "FPCh", 0`
      - `int64_t SerumDSP::SavePreset(int64_t* arg1)`
    - Searching the decompiled binary for `XfsX`, showed the most relevant looking code snippets to be the following:
      - `char const data_67cfb0[0x5] = "XfsX", 0`
      - `int64_t SerumDSP::SavePreset(int64_t* arg1)`
  - Searching for symbols mentioning 'save' there are a whole bunch of results, but after filtering out all of those prefixed with `_mus`, `juce`, `_sqlite`, etc; the ones that looked most potentially interesting to me were:
    - `Symbiosis::saveProperties(void const*, FSRef const*)`
    - `VSTGUI::CDrawContext::saveGlobalState()` / `VSTGUI::CDrawContext::restoreGlobalState()`
    - `VSTGUI::CGDrawContext::saveGlobalState()` / `VSTGUI::CGDrawContext::restoreGlobalState()`
    - `int64_t SerumGUI::SavingPresetStuff(void* arg1)`
      - Basically only contained the following:
        - `SerumGUI::DoDialog(arg1, "Serum Demo version", "Sorry, the demo does not save presets!", 0) __tailcall`
    - `int64_t SerumGUI::Save_Buffer_To_File(void* arg1)`
      - Basically only contained the following:
        - `SerumGUI::DoDialog(arg1, "Serum Demo version", "Sorry, the demo does not save tables!", 0)`
    - `int64_t SerumDSP::saveDataBufferToWav(void* arg1)`
      - `return SerumDSP::makeDialog(arg1, "Save Aborted!!", "Sorry, the demo version does not allow you to export wav files.", &data_6b5d74, 0, (zx.o(0)).d) __tailcall`
    - `int64_t SerumDSP::SaveFXRackSettings(int64_t* arg1)`
      - Seems to use the magic bytes `FXRK` as a header when writing the file
      - Called from the `SerumGUI::notify` function 
    - `int64_t SerumDSP::SaveFXSingleSettings(void* arg1, char arg2)`
      - Seems to use the magic bytes `FXRS` as a header when writing the file
      - Called from the `SerumGUI::notify` function 
    - `int64_t SerumDSP::SaveMIDIMap(void* arg1)`
    - `int64_t SerumDSP::SaveShape_Old(void* arg1, char arg2)`
    - `int64_t SerumDSP::SaveShape_New(void* arg1, int32_t arg2)`
      - Seems to use the magic bytes `SERUMSHP`
    - `int64_t SerumDSP::SavePreset(int64_t* arg1)`
      - ```
        __builtin_strncpy(dest: rax_14, src: "CcnK", n: 8)
        __builtin_memcpy(dest: rax_14 + 8, src: "\x46\x50\x43\x68\x00\x00\x00\x01\x58\x66\x73\x58\x00\x00\x00\x01\x00\x00\x00\x01", n: 0x14)
        ```
        - This seems to use the magic bytes `CcnK`, and then within the hex of the `__builtin_memcpy`, it also includes the magic bytes `FPCh` and `XfsX`
  - Searching for symbols mentioning 'load' there are a whole bunch of results, but after filtering out all of those prefixed with `juce`, `_sqlite`, etc; the ones that looked most potentially interesting to me were:
    - `void* Symbiosis::VSTPlugIn::loadFXPOrFXB(void* arg1, int64_t arg2, int32_t* arg3)`
      - Called from:
        - `int64_t Symbiosis::SymbiosisComponent::convertVSTPreset(void* arg1, int64_t arg2, char arg3)`
        - `void* Symbiosis::SymbiosisComponent::auSetProperty(void* arg1, int32_t arg2, int32_t arg3, int32_t arg4, int32_t* arg5, int32_t arg6)`
    - `int64_t Symbiosis::SymbiosisComponent::loadConfiguration(void* arg1)`
    - `int64_t Symbiosis::loadFromFile(int64_t arg1, int64_t* arg2)`
      - Called from:
        - `int64_t Symbiosis::SymbiosisComponent::convertVSTPreset(void* arg1, int64_t arg2, char arg3)`
        - `int64_t Symbiosis::SymbiosisComponent::loadFactoryPresets(void* arg1, int64_t arg2)`
        - `int64_t Symbiosis::SymbiosisComponent::readParameterMapping(void* arg1, int64_t arg2)`
    - `int64_t Symbiosis::SymbiosisComponent::loadFactoryPresets(void* arg1, int64_t arg2)`
      - Called from:
        - `int64_t Symbiosis::SymbiosisComponent::loadOrCreateFactoryPresets(void* arg1)`
    - `int64_t Symbiosis::SymbiosisComponent::loadOrCreateFactoryPresets(void* arg1)`
      - Mentions `SYFactoryPresets.txt`
    - `int64_t AudioEffectX::beginLoadBank() __pure`
      - This seems to be an empty function.. patched out in the demo version maybe?
    - `int64_t AudioEffectX::beginLoadProgram() __pure`
      - This seems to be an empty function.. patched out in the demo version maybe?
    - `uint64_t PresetManager::LoadDBAtPath(char** arg1, char* arg2, int64_t arg3)`
      - Called from:
        - `int64_t SerumGUI::PlotDBListInPresetBrowser(void* arg1, int32_t arg2, int32_t arg3, int64_t arg4)`
        - `int64_t SerumGUI::checkDefaultPath(int64_t* arg1, char arg2)`
          - Seems to check a paths that include:
            - `/System/user.dat`
            - `System/presetdb.dat`
            - `/Library/Audio/Presets/Xfer Records/Serum Presets/`
          - And call functions like:
            - `SerumGUI::PopulateWaveTableMenus(arg1)`
            - `SerumGUI::RefreshFilesToVector(arg1, &var_a68, 2)`
            - `SerumGUI::PopulateTableMenuOfType(arg1, 2)`
            - `SerumGUI::updateLFOShapeMenus(arg1)`
            - `SerumGUI::updateFXUnitsMenus(arg1)`
            - `SerumGUI::Formulas_Init(arg1)`
            - `PresetManager::LoadDBAtPath(arg1[0xc], &var_668, &var_a68)`
            - `SerumGUI::sqlte_CheckDBHeader(arg1, rsi_27, rdx_12, 1)`
            - `SerumGUI::updatePresetMenu(arg1, 1)`
            - `SerumGUI::updateTableMenuCheckmarks(arg1, 0)`
    - `uint64_t SerumGUI::LoadExec_This_Sound_From_File(void* arg1, char* arg2, int32_t arg3, int32_t arg4, int32_t arg5)`
      - Called from:
        - `int64_t SerumGUI::valueChanged(int64_t* arg1, int64_t* arg2, double arg3[0x2] @ zmm0)`
        - `uint64_t SerumGUI::notify(int64_t* arg1, int64_t arg2, int64_t arg3, uint32_t arg4[0x4] @ zmm0)`
        - `int64_t SerumGUI::doEvenIfClosedIdle(int64_t* arg1)`
      - Calls functions like:
        - `SerumGUI::ParsePathFromMediaBayXML(rdi_1, arg2)`
        - `SerumGUI::CheckIfValidSoundFile(_strcat(&var_438, i_1 + 0x15), &var_438)`
    - `void SerumGUI::LoadWT(void* arg1, int32_t arg2, int16_t arg3)`
    - `void SerumGUI::setFlagForPresetLoadFromDSP(void* arg1, int32_t arg2)`
    - `int64_t SerumDSP::DoXPlatLoadStuff(int64_t* arg1, char* arg2, int32_t arg3, int32_t arg4, int64_t arg5, char arg6)`
      - Called from:
        - `int64_t SerumDSP::setParameter() __pure`
        - and seemingly potentially other places too
      - Calls functions like:
        - `SerumDSP::ImportWT(r14_1, arg2, r15_1)`
        - `SerumDSP::ImportWTS(r14_1, arg2, r15_1)`
        - `SerumDSP::ImportAWV(r14_1, arg2, r15_1, 0)`
        - `SerumDSP::ImportAWV(r14_1, arg2, r15_1, 1)`
        - `SerumDSP::ImportKRI(r14_1, arg2, r15_1)`
        - `SerumDSP::ImportMF2(r14_1, arg2, r15_1)`
        - `SerumDSP::Import256(r14_1, arg2, r15_1)`
        - `SerumDSP::ImportWDF(r14_1, arg2, r15_1, rbx.d)`
        - `SerumDSP::ImportWAVETABLE(r14_1, arg2, r15_1)`
        - `SerumDSP::ImportPNG2WT(r14_1, arg2, r15_1)`
        - `SerumDSP::LoadPreset(arg1)`
        - `SerumGUI::setWaveCustomEdited(rdi_37, arg5.d, 1)`
    - `int64_t SerumDSP::LoadTuningFile(void* arg1, int32_t arg2)`
      - Called from:
        - `uint64_t SerumGUI::notify(int64_t* arg1, int64_t arg2, int64_t arg3, uint32_t arg4[0x4] @ zmm0)`
        - and seemingly potentially other places too
      - Calls functions like:
        - `CTuningMap::ReadFromFile(arg1 + 0x122940, *(arg1 + 0x39520))`
    - `int64_t SerumDSP::DoNoiseLoad(void* arg1, char* arg2, char arg3, int32_t arg4)`
      - Called from:
        - `int64_t SerumDSP::setParameter() __pure`
        - `int64_t SerumDSP::initNoiseTable(void* arg1, char arg2)`
          - Reads from paths like:
            - `/Library/Audio/Presets/Xfer Records/Serum Presets/`
            - `Organics/AC hum1.wav`
            - `Noises`
      - Calls functions like:
        - `SerumDSP::calculateNoiseTable(arg1, r13_9, i_37.d, r14_11)`
    - `uint64_t SerumDSP::LoadPreset(int64_t* arg1)`
      - Called from:
        - `int64_t SerumGUI::doEvenIfClosedIdle(int64_t* arg1)`
        - `int64_t SerumDSP::DoXPlatLoadStuff(int64_t* arg1, char* arg2, int32_t arg3, int32_t arg4, int64_t arg5, char arg6)`
        - `int64_t SerumDSP::CheckForDefaultFXPAndLoad(int64_t* arg1)`
        - `int64_t SerumDSP::LoadRandomizedPreset(int64_t* arg1, int32_t arg2, int64_t* arg3)`
    - `int64_t SerumDSP::LoadShape_New(int64_t* arg1, char arg2, char arg3, uint128_t arg4 @ zmm0, uint64_t arg5[0x2] @ zmm1)`
      - ```
        if (_strncmp(rax_3, "SERUMSHP", 8) != 0)
        _free(rax_3)
        return SerumDSP::LoadShape_Old(arg1, zx.d(rbx_1), arg3) __tailcall
        ```
      - Called from:
        - `int64_t SerumDSP::setParameter() __pure`
    - `int64_t SerumDSP::LoadShape_Old(int64_t* arg1, int32_t arg2, char arg3)`
      - Called from:
        - `int64_t SerumDSP::LoadShape_New(int64_t* arg1, char arg2, char arg3, uint128_t arg4 @ zmm0, uint64_t arg5[0x2] @ zmm1)`
    - `int64_t SerumDSP::CheckForDefaultFXPAndLoad(int64_t* arg1)`
      - `Presets/User/default.fxp`
      - Called from:
        - `int64_t SerumDSP::setParameter() __pure`
        - `int64_t SerumDSP::SerumDSP(int64_t* arg1, int64_t arg2)`
    - `int64_t SerumDSP::CheckForDefaultMIDIMapAndLoad(void* arg1)`
      - `System/MIDI CC Maps/default.mmp`
      - Called from:
        - `int64_t SerumDSP::SerumDSP(int64_t* arg1, int64_t arg2)`
    - `int64_t SerumDSP::LoadMIDIMap(void* arg1)`
      - Called from:
        - `uint64_t SerumGUI::notify(int64_t* arg1, int64_t arg2, int64_t arg3, uint32_t arg4[0x4] @ zmm0)`
        - `int64_t SerumDSP::CheckForDefaultMIDIMapAndLoad(void* arg1)`
    - `int64_t SerumDSP::CheckForProgramChangeMapAndLoad(void* arg1)`
      - `System/ProgramChanges.txt`
      - Called from:
        - `int64_t SerumDSP::SerumDSP(int64_t* arg1, int64_t arg2)`
    - `int64_t SerumDSP::LoadRandomizedPreset(int64_t* arg1, int32_t arg2, int64_t* arg3)`
      - Called from:
        - `int64_t SerumGUI::doEvenIfClosedIdle(int64_t* arg1)`
    - `int64_t SerumDSP::LoadFXSingleSettings(int64_t* arg1, int32_t arg2)`
      - Called from:
        - `int64_t SerumGUI::valueChanged(int64_t* arg1, int64_t* arg2, double arg3[0x2] @ zmm0)`
        - `uint64_t SerumGUI::notify(int64_t* arg1, int64_t arg2, int64_t arg3, uint32_t arg4[0x4] @ zmm0)`
    - int64_t SerumDSP::LoadFXRackSettings(int64_t* arg1)
      - Called from:
        - `uint64_t SerumGUI::notify(int64_t* arg1, int64_t arg2, int64_t arg3, uint32_t arg4[0x4] @ zmm0)`
  - Some other random potentially interesting locations
    - `int64_t** queryUpdateServer(int64_t** arg1, int64_t* arg2, int32_t* arg3, char* arg4)`
      - ```
        https://xferrecords.com/api/update_check/?version=&os=&plugin_type=&host=&hostver=&tstamp=

        X-API-Key: organist-diction-model-molehill
        Content-Type: application/json
        Accept: application/json; version=1
        ```
    - `uint64_t SerumGUI::sNhBe(int64_t* arg1, int32_t arg2)`
      - https://www.youtube.com/watch?v=6Ma0pBeCDfc
    - `void SerumGUI::idle(int64_t* arg1)`
      - ```
        int64_t rax
        int64_t var_18 = rax
        if (arg1[4] != 0 && arg1[0x205].b != 0)
            if (arg1[0x63b].b == 0)
                SerumGUI::doIdle(arg1)
            if ((arg1[0x63b].b == 0 && arg1[0x63e].b == 0) || (arg1[0x63b].b != 0 && arg1[0x63e].b == 0))
                int64_t rcx_1
                char const* const rdx_1
                char const* const rsi_1
                int64_t* rdi_1
                if (*(arg1[1] + juce::LookAndFeel_V3::getTreeViewIndentSize) == 0)
                    rsi_1 = "\n Demoversion has timed out!"
                    rdx_1 = "Please remove and re-insert Serum"
                    rdi_1 = arg1
                    rcx_1 = 0x65
                else
                    rsi_1 = "Thank you for trying the Serum Demo!"
                    rdx_1 = "The demo does not save, and stops producing sound after 20 minutes per use."
                    rdi_1 = arg1
                    rcx_1 = 0x64
                SerumGUI::DoDialog(rdi_1, rsi_1, rdx_1, rcx_1)
            arg1[0x63e].b = 1
        ```
    - `uint64_t SerumGUI::notify(int64_t* arg1, int64_t arg2, int64_t arg3, uint32_t arg4[0x4] @ zmm0)`
      - ```
        if (VSTGUI::CVSTGUITimer::kMsgTimer == arg3)
            r13 = 1
            if (arg1[0x63b].b != 0)
                SerumGUI::doIdle(arg1)
        else
        ```
      - `if (VSTGUI::CNewFileSelector::kSelectEndMessage == arg3)`
      - in the `else` block of `if (arg2 == 0)`
      - somewhere nested after that it mentions strings like:
        - ```
          (*(rcx_60 + 0x2e0))(rax_106, "Enter number of samples per frame", "Click \'Guess\' to have Serum guess frame size from pitch.", rcx_60)
          __builtin_strncpy(dest: arg1[0x3b8] + 0x1ea, src: "2048", n: 5)
          ```
      - under `label_4f663f`
        - `SerumDSP::LoadFXSingleSettings(arg1[1], zx.q(r14_4))`
      - then in various other parts of the function
        - `SerumGUI::checkDefaultPath(arg1, 0)`
        - `SerumDSP::LoadMIDIMap(arg1[1])`
        - `SerumDSP::LoadTuningFile(arg1[1], 0)`
        - `SerumDSP::LoadFXRackSettings(arg1[1])`
        - `SerumGUI::LoadExec_This_Sound_From_File(rdi_7, rsi_4, rdx_13, rcx_12, 0)`
        - `SerumGUI::Export_Buffer_To_256(arg1, rbx_3.d, 1, *(arg1[1] + 0x39520), arg4[0])`
        - under `label_4f6214` (and in another place close by)
          - `SerumGUI::DoDialog(arg1, "Serum Demo version", "Sorry, the demo does not save tables!", 0)`
        - under `label_4f6350`
          - `SerumGUI::SavingTableStuff(arg1, r8_1.d - 9, 0, 0, 1, arg4[0])`
        - ```
          if (rax_46 != 0)
              _fclose(rax_46)
              _strcpy(&var_338, *(arg1[1] + 0x39520))
              EditorFileNameOnly(&var_338, 0)
              __builtin_strcpy(dest: &var_338 + _strlen(&var_338), src: " already exists! Do you want to replace it?")
              r13 = 1
              SerumGUI::DoDialog(arg1, &var_338, "Click Cancel to Cancel save, or …", 1)
          else
              label_4f6380:
              SerumGUI::DoDialog(arg1, "Serum Demo version", "Sorry, the demo does not save presets!", 0)
              r13 = 1
          ```
    - `int64_t SerumGUI::CheckIfFileExists(int64_t arg1, int64_t arg2)`
    - `int64_t SerumGUI::CheckIfFileExistsAndEnumerate(int64_t arg1, int32_t* arg2, char arg3)`
  - `Symbiosis::VSTPlugIn::loadFXPOrFXB`
    - https://github.com/blurkk/symbiosis-au-vst-2
      - > Symbiosis is a developer tool for adapting Mac OS X VST plug-ins to the Audio Unit (AU) standard.
      - https://github.com/blurkk/symbiosis-au-vst-2/blob/af6afdeec3db421ef83b946981bb200db4beb973/Symbiosis.mm#L1629-L1730
        - Looking at `VSTPlugIn::loadFXPOrFXB(size_t size, const unsigned char bytes[])`, we can see that it reads in a bunch of header data, and then performs checks against it:
          - ```
            int magicID;
            int dataSize;
            int formatID;
            int version;
            int plugInID;
            int plugInVersion;
            bp = readBigInt32(bp, ep, &magicID);
            bp = readBigInt32(bp, ep, &dataSize);
            bp = readBigInt32(bp, ep, &formatID);
            bp = readBigInt32(bp, ep, &version);
            bp = readBigInt32(bp, ep, &plugInID);
            bp = readBigInt32(bp, ep, &plugInVersion);
            ```
          - `magicID` should generally equal `CcnK` (which it seems to be in Serum presets)
          - `formatID` should be one of:
            - `FxCk`: FXP parameter list
            - `FPCh`: FXP custom chunk (which it seems to be in Serum presets)
              - ```
                bp += 4;
                char programName[24 + 1];
                strncpy(programName, reinterpret_cast<const char*>(bp), 24);
                programName[24] = '\0';
                setCurrentProgramName(programName);
                bp += 28;
                int chunkSize;
                bp = readBigInt32(bp, ep, &chunkSize);
                ```
            - `FxBk`: FXB program list
            - `FBCh`: FXB custom chunk
          - etc
        - `VSTPlugIn::loadFXPOrFXB` also calls `const unsigned char* VSTPlugIn::readFxCk(const unsigned char* bp, const unsigned char* ep, bool* wasPerfect)` at various points
          - https://github.com/blurkk/symbiosis-au-vst-2/blob/af6afdeec3db421ef83b946981bb200db4beb973/Symbiosis.mm#L1447C1-L1505
        - We could potentially parse this in python or similar:
          - https://docs.python.org/3/library/struct.html
            - > This module converts between Python values and C structs represented as Python bytes objects. Compact format strings describe the intended conversions to/from Python values.
            - https://docs.python.org/3/library/struct.html#struct.unpack
            - https://docs.python.org/3/library/struct.html#struct.unpack_from
            - https://docs.python.org/3/library/struct.html#struct.iter_unpack
            - https://docs.python.org/3/library/struct.html#format-strings
  - `SerumDSP::SavePreset`
  - `SYParameters.txt`
    - See parsed/converted docs and other notes/links here: https://forum.vital.audio/t/idea-convert-serum-presets-to-vital/2580/16?u=devalias
      - > After a little digging around, I found that the `SYParameters.txt` file seems to relate to the `symbiosis-au-vst` lib:
        > 
        > - `https://code.google.com/archive/p/symbiosis-au-vst/`
        >     - `https://code.google.com/archive/p/symbiosis-au-vst/wikis/Introduction.wiki`
        >     - `https://code.google.com/archive/p/symbiosis-au-vst/wikis/SymbiosisInUse.wiki`
        >     - `https://groups.google.com/g/symbiosis-au-vst`
        > 
        > Symbiosis seems to be an old software library allowing VST's to easily convert to/interact with the AU format.
        > 
        > In particular, I was looking deeper at this fork of the code, and noticed it mentions `SYParameters.txt` in a few places:
        > 
        > - `https://github.com/blurkk/symbiosis-au-vst-2`
        >     - `https://github.com/search?q=repo%3Ablurkk%2Fsymbiosis-au-vst-2+SYParameters.txt&type=code`
        >         - In file: `Symbiosis.mm`, mentioned in function:
        >             - `void SymbiosisComponent::readParameterMapping(const ::FSRef* fsRef)`
        >         - In file: `documentation/Symbiosis Documentation.html`
        >             - See below for more info
        >         - Also mentioned in 2 other files, but they seemed less interesting
        > 
        > Here is the relevant info on this file format extracted from the `Symbiosis Documentation.html` docs:
        > 
        > > Advanced Porting Options
        > > ------------------------
        > >
        > > Symbiosis creates two configuration files inside your AU bundle the first time it is launched: `SYParameters.txt` and `SYFactoryPresets.txt`. It will also create `.aupreset` files for all the VST programs in the initial startup bank. All these files are created directly under `Contents/Resources/` in your bundle.
        > >
        > > It is a good idea to edit at least `SYParameters.txt` and you should include all the created files in the final distribution of your Audio Unit. (Please read an important note concerning this under 'Running Your AU for the First Time'.) If you are using wrapping alternative 3, 4, or 5 (including Symbiosis.mm etc into your VST project) you can simply drop the files into your project and they will be copied in the build process.
        > >
        > > Finally, if you are serious about creating a fully featured Audio Unit you might want to look into supporting Symbiosis' optional 'Vendor-Specific Extensions' below.
        > >
        > > ### `SYParameters.txt`
        > >
        > > This file is a tab-separated table with parameter information. One line per parameter with an extra header line at the top. You may choose to exclude certain parameters from the AU version by simply removing the corresponding lines from this file.
        > >
        > > The columns in this file are as follows:
        > >
        > > | Column | Description |
        > > | --- | --- |
        > > | vst param # | The VST parameter number (zero-based), which is also the unique identifier for the parameter.^1 |
        > > | name | The parameter name as shown to the end user.^2 |
        > > | min | The minimum parameter value.^3 |
        > > | max | The maximum parameter value.^3 |
        > > | display | A string that defines how the parameter is displayed to the end user. Use one of the following: |
        > > |  | `=` for linear scaling (within the `min` to `max` range). |
        > > |  | `b` for boolean switch (0 is off, 1 is on) |
        > > |  | `i` for integer (scaled from `min` to `max`) |
        > > |  | a|b|c|d for discrete parameter settings, e.g. `sine|tri|saw|pulse` |
        > > |  | `?` to convert the value with the 'Vendor-Specific Extensions' (described below). |
        > > | unit | The parameter suffix / unit. |
        > > | default | The initial default setting. (Scaled according to `min` and `max` range.) |
        > >
        > > ^1: If changes to this parameter will automatically modify other parameters you need to suffix this column with `+`. This information is important for AU hosts.\
        > > ^2: You may wish to edit this column as AU can handle longer parameter names than VST.\
        > > ^3: VST parameter values are always between 0 and 1, but AU parameters have arbitrary range. The min and max values are used to scale and normalize the AU parameter range from/to the 0 and 1 range. For discrete parameters (those having `|`-delimited lists in the `display` column) the `min` value must be 0 and the `max` value should be the count of discrete options minus one, e.g. `3` if there are four choices.
        > >
        > > ### `SYFactoryPresets.txt`
        > >
        > > This file simply contains a list of factory preset files (one file name per row). You can edit this file to remove or add factory presets. Symbiosis expects to find the factory preset files under `Contents/Resources/` (as always).
    - `/Library/Audio/Plug-Ins/Components/Serum.component/Contents/Resources/SYParameters.txt`
    - https://github.com/blurkk/symbiosis-au-vst-2/blob/af6afdeec3db421ef83b946981bb200db4beb973/Symbiosis.mm#L2461-L2485
    - https://github.com/blurkk/symbiosis-au-vst-2/blob/af6afdeec3db421ef83b946981bb200db4beb973/documentation/Symbiosis%20Documentation.html#L173C1-L250C131
- https://unison.audio/reverse-engineer-presets-in-serum/
  - > A Complete Guide To Reverse-Engineering Any Preset In Serum
- https://xferrecords.com/forums/general/file-types
  - > Serum presets will show "XfsX" for the 16-20th chars of the file
  - > Serum preset file format is complex/programmatic and isn't public. I hope to make it more open in the future / new format with conversion or import.
    > 
    > There is public info on the Serum wavetable format.
    > This is an example 'clm ' chunk from a Serum-created wavetable (.wav) File:
    > 
    > <!>2048 01000000 wavetable (www.xferrecords.com)
    > Serum currently assumes 2048 (samples per frame) at all times, so as of now 2048 should always be written there.
    > 
    > Only the two first flags are currently used:
    > 
    > - the first flag is the WT interpolation [0 = no interpolation, 1 = linear crossfades, 2,3,4 = spectral morph]
    > - the second flag is "Serum Factory WT" which means Serum assumes this file comes with Serum and everyone already has it - thus it will not embed in to user presets to keep file sizes down. PLEASE DO NOT ENABLE THIS FLAG IF YOU ARE CREATING WAVETABLES - please leave it to zero, thank you very much. If you want a similar flag for yourself to identify tables as factory or otherwise for your product, drop me a line and I will reserve you a flag or a different value on that flag.
  - https://xferrecords.com/forums/general/file-types#post_80648
    - See my PoC code for enumerating the synth plugin settings + extracting patch details via Spotify's pedalboard in this comment
- https://www.reddit.com/r/edmproduction/comments/69hxa7/reverse_engineering_serums_fxp_files/
  - > I'm trying to build a program to generate new presets for Serum. Serum stores them as a .fxp file, which seems to be a header followed by opaque data. Is there documentation on how to extract parameter values from these files somewhere, or am I out of luck?
  - > Update: I reached out to Steve through Xfer's forum and he was prompt and helpful. Unfortunately, the .fxp file format is completely dependent on the source code, and he can't release a spec for it without making the code open source. Which probably isn't happening any time soon.
  - > You can reverse engineer by exporting fxp files for every parameter change to create a spec that would produce compatible presets. Then build your program using VST SDK's fxProgram struct.
    >
    > I would try first with a simple plugin with just couple values OR just ask the dev to open the code, some strictly forbid decompiling their software :V
  - > Exactly, it seems like those are the only options unfortunately. I've heard some have success with doing changing a parameter value in the .fxp file, and successfully using that preset in Serum. I'm just annoyed that the process can't be automated.
- https://forum.vital.audio/t/idea-convert-serum-presets-to-vital/2580
  - > Idea: Convert Serum presets to Vital
    > As Serum and Vital seem to share quite a lot of common ground, I was thinking - would it be possible to write a script that converts Serum presets and wavetables to Vital?
  - > You can copy the serum wavetable and sample files into your vital folders. Works fine
  - > I have tried to convert some, but vital lacks an effect device like the expander/unison tool in Serum.
    > also, remapping and reverb lfos which Serum patches make use of alot, do not exist in Vital yet.
    > vital sounds very warm somehow, whereas Serum is crisp by default. two very different souls of equal beauty
  - > I had a similar thought, but after I tried to implement several Serum patches manually on Vital, I came to the conclusion that many items are not a simple conversion, due to several differences which could not be realized on one synth or the other. The other problem is the saved preset format. Vital presets are saved as text files with all the parameters listed out in human readable form. Serum presets are saved in a binary format, which are machine readable, and unless someone on the net has a map to how this is done, you would have to reverse engineer it yourself - which is a big project. But, I’ll tell you how I would start: save an Init patch, then begin by changing one knob at a time, save the preset and inspect the values in the preset file. You will begin to see what the pattern is, then you would have to write a program to convert the Serum preset into text. Once you had most of the parameters covered, you could begin to correlate the values of one synth against the other. Then, you could start devising a method to import that preset text into Excel or some spread sheet program. Some of the values do not have a one to one correlation between each other, so you would need to come up with formulas to convert Serum values to the similar Vital values. There are many parameters that translate easier than others. Osc and filter values are pretty easy to figure out, except for exclusive features, and others like the effects, as noted in another post, are just different and cannot be done. A few of the complex filters in Serum can be realized by cascading the 2 filters in Vital, but not all of them. Try converting a well documented Serum patch to Vital yourself, and you’ll likely begin to see the problems. My bottom line is I’m going to have to buy Serum if I want to make those sounds easily
  - https://forum.vital.audio/t/idea-convert-serum-presets-to-vital/2580/14?u=devalias
    - See my PoC code for enumerating the synth plugin settings + extracting patch details via Spotify's pedalboard in this comment
- https://www.kvraudio.com/forum/viewtopic.php?t=420599&start=2355
  - > As you know, Serum's preset manager, while being one of the best of many VSTs out there, it's still lacking in basic features such as delete. Save on spot without full database re-scan and etc etc.
    >
    >However over time I've been given so many presets for serum via signups to newsletters or those that come with sample packs etc that I've got more SHAIT presets than good ones, not to mention those annoying duplicates with just different names. So I wrote a little tool to get rid of all the shit.
    >
    >https://github.com/DarceyLloyd/serum-preset-collector
    >
    >The instructions are on the page on how to use it, just make backups before you start making all your changes of noises, wavetables, presets and the serumdatabase.dat file (sqlite database file).
    >
    >I would have wrote something to organise the noise and wavetable folders also but I can't be arsed to decode the fxp file format that serum uses to do that... Maybe in the future... Real shame Serum can't scan the noise and wavetable folders for each preset with missing noise & wavetable files and allow a bulk re-save on this.

## Parsing preset files from code (`.fxp`/`.fxb`/`.vstpreset`)

- https://en.wikipedia.org/wiki/Virtual_Studio_Technology#Presets
  - > VST plugins often have many controls, and therefore need a method of managing presets (sets of control settings).
    > 
    > Steinberg Cubase VST introduced two file formats for storing presets: an FXP file stores a single preset, while an FXB file stores a whole bank of presets. These formats have since been adopted by many other VST hosts, although Cubase itself switched to a new system of preset management with Cubase 4.0.
    > 
    > Many VST plugins have their own method of loading and saving presets, which do not necessarily use the standard FXP/FXB formats.
- https://fileinfo.com/extension/fxp
  - > An FXP file is a preset used by audio-mixing applications that support Virtual Studio Technology (VST). It contains an individual audio effect that can be added to a Digital Audio Workstation (DAW) via a VST plug-in. FXP files are related to .FXB files, which contain multiple presets.
- https://fileinfo.com/extension/fxb
  - > An FXB file is a soundbank used by audio-mixing applications that support Virtual Studio Technology (VST). It contains presets that allow Digital Audio Workstations (DAWs) to produce additional sound effects, which are loaded within VST plug-ins. FXB files are used to install multiple presets, while .FXP (FX Preset) files are used to install individual presets.
- https://fileinfo.com/extension/vstpreset
  - > A VSTPRESET file is a preset file used by audio-mixing applications that support the Virtual Studio Technology 3 (VST 3) plug-in standard, such as Steinberg Cubase. It contains one or more audio effects that can be loaded in a VST 3 plug-in. VSTPRESET files may also contain descriptive tags, such as Acoustic, Clean, and Percussive, that help users organize and search for presets.
  - > NOTE: VSTPRESET files replaced `.FXP` and `.FXB` files.
- https://forums.steinberg.net/t/fxp-specifications/201946/2
- https://steinbergmedia.github.io/vst3_doc/vstsdk/classSteinberg_1_1Vst_1_1PresetFile.html
- https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.VST3Plugin.load_preset
  - `load_preset(preset_file_path: str) → None`
    - > Load a VST3 preset file in `.vstpreset` format. 
- https://github.com/demberto/fxp
  - > VST2.x plugin FXP preset parser
  - https://fxp.readthedocs.io/en/latest/
- https://github.com/danielappelt/fxbconv
  - > Converts FXB bulk plugin preset files into individual FXP, or Carla preset files
- https://github.com/SpotlightKid/ardour2fxp
  - > Convert between Ardour XML and binary FXP VST2 preset files.

## Rendering a Vital Synth Patch to audio from CLI

- https://www.reddit.com/r/VitalSynth/comments/16hrx39/has_anyone_used_vital_in_headless_mode/
  - https://www.reddit.com/r/VitalSynth/comments/16hrx39/comment/k86801j/
  - See my comment for more specific details, but the most relevant snippets are below.
  - ```
    ⇒ /Applications/Vital.app/Contents/MacOS/Vital --help
    Usage:
      Vital [OPTION...]

    Vital polyphonic wavetable synthesizer.

    Help Options:
      -h, --help                          Show help options

    Application Options:
      -v, --version                       Show version information and exit
      --headless                          Run without graphical interface.
      --tabletowav                        Converts a vitaltable to wav file.
      --tableimages                       Renders an image for the table.
      --render                            Render to an audio file.
      -m, --midi                          Note to play (with --render).
      -l, --length                        Not length to play (with --render).
      -b, --bpm                           BPM to play (with --render).
      --images                            Render oscilloscope images (with --render).

    ⇒ cd ~/Desktop

    ⇒ /Applications/Vital.app/Contents/MacOS/Vital --render "/Users/devalias/Music/Vital/Factory/Presets/Plucked String.vital" --midi 48 --length 3 --bpm 120 --images
    ```
  - > Though unfortunately, when I tried to do that, it seems to get a segmentation fault and crash:
    - ```
      Thread 0 Crashed:: JUCE Message Thread Dispatch queue: com.apple.main-thread
      0   Vital                                  0x105b4a238 juce::AudioFormatWriter::writeFromFloatArrays(float const* const*, int, int) + 40
      1   Vital                                  0x105efb2ac SynthBase::renderAudioToFile(juce::File const&, float, float, std::__1::vector<int, std::__1::allocator<int>>, bool) + 3132
      2   Vital                                  0x105ce39be processCommandLine(juce::String const&) + 6334
      3   Vital                                  0x105e59ffa StandaloneSynth::initialise(juce::String const&) + 570
      4   Vital                                  0x105b8c7e2 juce::JUCEApplicationBase::initialiseApp() + 1042
      5   Vital                                  0x105cbed5b juce::JUCEApplication::initialiseApp() + 11
      6   Vital                                  0x105b4a578 main + 216
      7   dyld                                0x7ff806ac241f start + 1903
      ```
  - > And from ChatGPT, analysing the full segfault crash report, gives the following explanation:
    - ```
      The crash report indicates that the application Vital crashed due to a segmentation fault (SIGSEGV), which is a type of crash where a program attempts to access a restricted area of memory.

      Here are the key points from the crash report:

      - **Process**: Vital (audio.vital.synth)
      - **Version**: 1.5.5
      - **Crashed Thread**: 0 JUCE Message Thread (main thread)
      - **Exception Type**: EXC_BAD_ACCESS (SIGSEGV)
      - **Exception Codes**: KERN_INVALID_ADDRESS at 0x0000000000000018

      The crash occurred in thread 0, which is the main thread of the application. The function call stack indicates that the crash happened during a call to `juce::AudioFormatWriter::writeFromFloatArrays`, which is a function from the JUCE framework used to write audio data. It appears that the application attempted to access memory at address `0x18`, which was not a valid address, leading to the segmentation fault.

      ..snip..
      ```
  - I raised this as a bug here: https://github.com/mtytel/vital/issues/45

## Unsorted

- https://www.reddit.com/r/synthrecipes/
  - > Where sound designers / synthesizer enthusiasts come to share and grow their skill set. Check our Wiki for the Synthrecipes Cookbook!
  - https://www.reddit.com/r/synthrecipes/comments/icvi6e/shouldnt_there_be_an_ai_app_by_now_that_you_can/
    - > Shouldn't there be an AI app by now that you can feed it a sound and automatically change your synth parameters to recreate that sound? Would you buy it? (2020)
- https://www.reddit.com/r/synthesizers/
  - > The place to obsess about synthesizers, both hardware and software.
  - https://www.reddit.com/r/synthesizers/comments/zatse3/open_ai_synth_advice/
    - > Open AI synth advice (2022)
- https://forum.vital.audio/t/idea-convert-serum-presets-to-vital/2580
  - > Idea: Convert Serum presets to Vital (2020)
- https://sound.stackexchange.com/questions/23983/what-is-the-most-effective-way-to-reverse-engineer-sysex-format-for-my-old-yamah
  - > What is the most effective way to reverse engineer SysEx format for my old Yamaha CS1x (2011)
- https://tools.splice.com/astra
  - > Astra by Splice
    > The inspirational polysynth with FM, wavetable, granular, analog, and sampler oscillator sources—plus limitless customizability, presets galore and deep integration with the Splice workflow.
  - https://splice.com/sounds/packs/four4/astra-epic-techno-presets/presets
    - > Googled for a random Splice Astra preset, ended up on this page, and while I can't download them, it very much looks as though they are just xml files:

## Musings

> Not sure how much music production stuff you've done, but if you're open to sharing a high level /2c on whether you think this is a practical thing, would be curious what your thoughts are on the idea of applying ML sort of concepts to 'audio generation', but not in a 'direct' way, so much as making synthesizer patches/presets/etc?

Some thoughts in that space would be:

- basic text prompt -> synth patch (likely vital at first because free, and ideally serum also, but I probably need to reverse engineer their patch binary format first; or extract that relevant details via another indirect method)
- 'clone'/'convert' a serum patch -> vital (or vice versa): not as simple as direct 1:1 parameter mapping from their file formats as they implement things differently, so I would imagine it might end up being sort of like a adversarial type thing to get 'closer' to the 'right' sound
- probably others, but that's what is 'top of mind' at the moment

---

On my ai synth gist, in the unsorted section there’s a few links to projects/blogs that have done synth patch generation stuff.

I was re-reading the one that did it for ableton analog the other day; it sounded like a decent starting point

But one of their future improvements things (and what I was also thinking) would be to somehow add some better feedback on the output sound back into the model; either based on the audio it produces, or the spectrogram of it or similar

I was also thinking there are some models that can label audio based on various moods/danceability/etc; that I figured maybe could be used to enrich the ‘metadata’ that goes into the training; but not sure if they would work on like simple synth sounds; as I suspect they need the full composition to figure those sorts of things

The other area I was thinking about was sort of in the space of GAN’s; and maybe being able to give it a sound you want to get a patch for; and having it be able to learn to adjust all the synth params to get as close as possible to that sound. Where the reward feedback would basically be how ‘close’ to the sound it could get

And then in a different area of AI useful; that’s there’s already at least 1 app for; and ableton 12 sounds like it added it; grouping/clustering existing samples and being able to search by vibe/qualities of them, find similar sounds, etc. As I always struggle to find the ‘right’ sounds that I want; without just going through everything and getting distracted along the way

Thing like splice’s create tool are also kind of a neat application:

- https://splice.com/sounds/create

Basically anything that helps me get from “I want to do a thing” to “oh, that’s got the creative juices going!”

---

I think what would be really neat if training a model on various presets, is if it could sort of 'bucket'/group the different synth presets so they are more tightly integrated, but potentially also train on multiple synths worth at the same time, so that it can maybe 'share the learnings' among them. I don't really know enough about how that works at a more deeper/technical level, but I'm pretty sure bucketing was one of the methods they used when training StableDiffusion on different image sizes/etc

---

From (private chat link): https://chat.openai.com/c/08e6d859-c270-460d-bb89-31c395dab661

> **Me:**
>
> I believe with some of the StableDiffusion training, they divided the training data into different 'buckets' based on the image size dimensions. I think they did this so that they could train on a larger set of data, while having the model 'learn better' aspects about the items in the 'bucket'. I think this was done so that the overall model could share knowledge about general concepts 'between' all of the buckets (rather than having individual models trained on the smaller datasets of each individual bucket), while also gaining some benefit from dividing the data into those buckets (eg. maybe it learned that data in those buckets was more correlated in a certain way that might not generalise across all buckets)
> 
> What do you think about my assumptions here? Are they grounded in reality? Are there  specific technical terms in machine learning / data science that refer to these concepts?

> **ChatGPT:**
> 
> Your understanding aligns quite well with certain concepts in machine learning and data science, particularly in the context of training models like StableDiffusion. Let's break down your assumptions and relate them to technical terms and practices:
> 
> 1. **Dividing Training Data into 'Buckets' Based on Image Size Dimensions**: This is a strategy often used in data preprocessing and is known as "data stratification" or "data bucketing." The idea is to create subgroups or 'buckets' within the data that share common characteristics (in this case, image size). This can help in managing memory usage and computational efficiency, especially when dealing with a diverse range of image sizes.
> 
> 2. **Training on a Larger Set of Data While Learning Specific Aspects in 'Buckets'**: This approach leverages the concept of "transfer learning." By training on a large dataset, the model learns general features and patterns. Then, by focusing on specific buckets, it can fine-tune its understanding of particular characteristics associated with those groups. This is common in deep learning where a model trained on a broad dataset is later fine-tuned on a more specific dataset.
> 
> 3. **Sharing Knowledge Between Buckets for General Concepts**: This is essentially the essence of "feature learning" in machine learning. The model learns to recognize and extract useful features or patterns that are applicable across different datasets or buckets. In neural networks, especially in layers closer to the input, the model tends to learn more general features that can be shared across different types of data.
> 
> 4. **Learning Correlations in Data Within Buckets That Might Not Generalize Across All Buckets**: This touches on the concept of "model specialization." Within each bucket, the model might learn nuances and patterns specific to that subgroup. However, these specialized patterns might not be applicable or might be less effective when applied to data outside that bucket. This is a balance between generalization (applying learned knowledge broadly) and specialization (focusing on specific patterns within a subgroup).
> 
> Your assumptions reflect a sophisticated understanding of how data stratification, transfer learning, feature learning, and model specialization can play roles in training complex models like those used in image generation. These strategies help in handling large and diverse datasets efficiently while aiming for both broad applicability and specialized proficiency.

- https://en.wikipedia.org/wiki/Data_binning
- https://developers.google.com/machine-learning/data-prep/transform/bucketing
- https://asq.org/quality-resources/stratification
  - > Stratification is defined as the act of sorting data, people, and objects into distinct groups or layers. It is a technique used in combination with other data analysis tools. When data from a variety of sources or categories have been lumped together, the meaning of the data can be difficult to see. This data collection and analysis technique separates the data so that patterns can be seen and is considered one of the seven basic quality tools.
- https://en.wikipedia.org/wiki/Transfer_learning
  - > Transfer learning (TL) is a technique in machine learning (ML) in which knowledge learned from a task is re-used in order to boost performance on a related task.
- https://en.wikipedia.org/wiki/Feature_learning
  - > In machine learning, feature learning or representation learning is a set of techniques that allows a system to automatically discover the representations needed for feature detection or classification from raw data.

> **Me:**
> 
> Ok, lets say we want to apply those concepts (or any other relevant concepts) to training an AI model on software synthesizer patch files, so that it can learn to generate synth patches based on inputs from a user.
> 
> There are many different synths out there, and each one uses a different format for their patch files; but many of the concepts they each use are very similar. Ideally we would like to be able to train the model with presets from a number of different synths, and to have it learn the general concepts of 'good patch design', as well as how to apply these concepts to the specifics required to implement in each individual synth's patch format.
> 
> It would also be great if based on those learnings, it was able to 'translate' a synth patch for one synthesizer, into the format of another synth; and have it generate the same (or very close to it) sound. This is complicated by the fact that different synths will have different internals for how they translate the synth patch into a sound; and so even if the patch files have similar parameters (eg. oscilators, wave shape, filters, etc), they probably won't be a 1 to 1 mapping between these parameters on different synths for the same sound.
> 
> It would also be cool if we could use an existing sound as an input, and have the model produce a patch file for a given synth that is able to re-create that sound (or something close to it)
> 
> I don't know if this would be relevant, but I was also thinking that it might be interesting/useful to be able to use existing models to enrich the 'metadata' of various sounds produced; ideally in a way that we can help teach the model better 'human words' for describing the 'feeling' or 'style' of various sounds.
> 
> Other things that might be cool to be able to do with a model like this, is a 'style transfer' sort of thing, where I can provide an existing synth patch and/or audio file, and some prompt text, and have the original modified in a way that makes it more like the prompt.

> **ChatGPT:**
> 
> You're envisioning an AI model that operates in a complex, multidimensional space, encompassing sound synthesis, format translation, audio analysis, and even semantic interpretation of audio characteristics. Here are some key machine learning and AI concepts that could be employed to realize such a system:
> 
> 1. **Transfer Learning and Feature Learning**: Given that different synthesizers use different patch formats, but share underlying concepts (like oscillators, waveforms, filters), a model could be trained to understand these common features. Transfer learning would allow the model to apply its understanding of synthesis concepts learned from one synth to another, despite differences in format.
> 
> 2. **Cross-Modal Learning for Patch Translation**: Translating a patch from one synth to another, where the internal sound generation mechanisms differ, requires the model to learn cross-modal mappings. This involves understanding how different parameter configurations in one synth correspond to those in another to produce similar sounds.
> 
> 3. **Audio Analysis and Reverse Engineering**: For the model to recreate a sound from an audio input, it needs to analyze the audio and reverse-engineer the parameters that might have produced it. This involves deep learning techniques in audio processing and synthesis.
> 
> 4. **Semantic Analysis and Metadata Enrichment**: Enriching the metadata of sounds with descriptors about their 'feeling' or 'style' involves natural language processing (NLP) and perhaps some form of sentiment analysis or style recognition. Training a model to understand and generate human-like descriptions of sounds involves bridging audio analysis with semantic language understanding.
> 
> 5. **Style Transfer and Generative Models**: Just like style transfer in images, this concept can be applied to audio. Here, the 'style' might refer to the characteristic sound of a synth patch. The model would need to understand the essence of a given sound and then apply this essence to modify another sound or synth patch according to a text prompt.
> 
> Implementing such a system would likely require a combination of deep neural networks for audio processing and synthesis, NLP models for semantic understanding, and potentially generative adversarial networks (GANs) for style transfer and patch generation tasks.
> 
> Given your background in software engineering and interest in AI, you might approach this project by:
> 
> - Collecting and preprocessing data from various synthesizers, ensuring a diverse range of sounds and patch formats.
> - Experimenting with existing models for audio analysis and synthesis, and adapting them to your specific use case.
> - Incorporating NLP techniques for semantic analysis and metadata enrichment.
> - Iteratively training and fine-tuning the model, potentially starting with a simpler task (like understanding patches from a single synth) and gradually increasing complexity.
> 
> This project would be quite ambitious, blending multiple complex domains of AI, but it's certainly an intriguing concept with potential for innovative developments in sound synthesis and audio AI.

> **Me:**
> 
> If we assume that the model itself doesn't need to directly generate any audio (as that could be done by using a generated patch with the synth itself); and we wanted to focus more specifically on the aspects of training the model to understand how to generate patches (ideally for different synths); would it make sense to collect all the patches for each synth into distinct 'buckets'?
> 
> Can you then also expand on more of the technical specifics that we should know about for implementing an algorithm that can learn to identify how each of these synth patches work? 
> 
> If the algorithm needs a 'feedback'/'reward' as part of training, what would be the best methods we could use for this, keeping in mind all of our original ideas/goals for this model? Would we be able to use the audio/similar output from the synth patch as part of the reward mechanism?

> **ChatGPT:**
> 
> Focusing on the generation of synth patches without the direct generation of audio simplifies the problem to an extent but still involves complex challenges. Here are some steps and technical specifics for implementing such a system:
> 
> ### Data Collection and Organization
> 
> 1. **Data Stratification**: Collecting patches for each synth and organizing them into distinct 'buckets' is a good approach. This allows the model to learn the specifics of each synth's patch format and the commonalities in sound synthesis across different synths.
> 
> 2. **Data Standardization**: Given that different synths have different patch formats, some level of standardization or normalization of data might be necessary. This could involve extracting and aligning comparable features from each patch format.
> 
> ### Learning Algorithm Implementation
> 
> 1. **Feature Extraction**: The model needs to understand the parameters in a synth patch and how they contribute to the final sound. Techniques like principal component analysis (PCA) or autoencoders could be used to identify the most relevant features in patches.
> 
> 2. **Neural Networks**: Deep learning models, particularly neural networks, could be well-suited for this task. Convolutional Neural Networks (CNNs) or Recurrent Neural Networks (RNNs) can be used, depending on the data's structure and the relationships you wish to model.
> 
> 3. **Transfer Learning**: If some synths share similar parameters or synthesis methods, transfer learning can be employed to leverage knowledge gained from one synth model to inform about others.
> 
> ### Feedback/Reward Mechanism
> 
> 1. **Supervised Learning with Audio Output**: If you can pair each patch with a recording of its audio output, you can use this as ground truth for supervised learning. The model can then be trained to generate patches that, when played on the respective synth, produce the desired audio.
> 
> 2. **User Feedback**: Implement a system where users can rate the quality or suitability of generated patches. This feedback can be used as a reward signal to improve the model iteratively.
> 
> 3. **Objective Metrics**: Develop objective metrics based on sound characteristics (like timbre, texture, or harmony) that define a 'good' patch. These metrics can guide the training process.
> 
> 4. **Reinforcement Learning**: If a clear reward signal can be established (like user ratings or adherence to objective metrics), reinforcement learning could be an approach. The model would learn to generate patches that maximize the reward signal.
> 
> ### Considerations for Implementation
> 
> - **Computational Resources**: Training deep learning models, especially those handling complex data like synth patches, requires significant computational resources.
> 
> - **Data Diversity**: Ensure that the dataset includes a wide variety of patches, covering a broad spectrum of sounds and styles, to encourage generalizability in the model.
> 
> - **Iterative Development**: Start with a simpler model, perhaps focusing on a single synth, and gradually expand to more complex scenarios and multiple synths.
> 
> - **User Interface**: Consider the design of the user interface, especially if you plan to incorporate user feedback into the training process.
> 
> Implementing such a model combines aspects of audio processing, machine learning, and user interaction. It's a challenging yet potentially rewarding project, especially given your background in software engineering and IT.

- https://en.wikipedia.org/wiki/Principal_component_analysis
- https://en.wikipedia.org/wiki/Autoencoder
- https://en.wikipedia.org/wiki/Variational_autoencoder
- https://en.wikipedia.org/wiki/Convolutional_neural_network
- https://en.wikipedia.org/wiki/Recurrent_neural_network

## See Also

### My Other Related Deepdive Gist's and Projects

- [Music APIs and DBs (0xdevalias' gist)](https://gist.github.com/0xdevalias/eba698730024674ecae7f43f4c650096#music-apis-and-dbs)
- [AI Voice Cloning / Transfer (eg. RVCv2) (0xdevalias' gist)](https://gist.github.com/0xdevalias/359f4265adf03b0142e4d0543c156a3e#ai-voice-cloning--transfer-eg-rvcv2)
- [Singing Voice Synthesizers (eg. Vocaloid, etc) (0xdevalias' gist)](https://gist.github.com/0xdevalias/0b64b25d72cbbc784042a9fdff713129#singing-voice-synthesizers-eg-vocaloid-etc)
- [Audio Pitch Correction (eg. autotune, melodyne, etc) (0xdevalias' gist)](https://gist.github.com/0xdevalias/7f4a5c31758e04aea5c2f5520e53accb#audio-pitch-correction-eg-autotune-melodyne-etc)
- [Automated Audio Transcription (AAT) / Automated Music Transcription (AMT) (aka: converting audio to midi) (0xdevalias' gist)](https://gist.github.com/0xdevalias/f2c6e52824b3bbd4fb4c84c603a3f4bd#automated-audio-transcription-aat--automated-music-transcription-amt-aka-converting-audio-to-midi)
- [Compare/Diff Audio Files (0xdevalias' gist)](https://gist.github.com/0xdevalias/91ae33e0c9290e69b457ce5034956fb7#comparediff-audio-files)
- [Working Around FLStudio Trial Limitations (0xdevalias' gist)](https://gist.github.com/0xdevalias/7c51aa2d862da34baaeecafb157e726c#working-around-flstudio-trial-limitations)
- [Reverse Engineering on macOS (0xdevalias' gist)](https://gist.github.com/0xdevalias/256a8018473839695e8684e37da92c25#reverse-engineering-on-macos)
